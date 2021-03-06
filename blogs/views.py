from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden
from .models import Post,Category
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import RegisterForm,LoginForm,PostForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from slugify import slugify



# Create your views here.

class IndexView(generic.ListView):
	paginate_by = 3
	model = Post
	template_name = 'blogs/index.html'
	context_object_name = 'latest_blog_list'
	def get_queryset(self):
		"""Return the last five published questions."""
		return Post.objects.filter(pub_date__lte = timezone.now(),status=1).order_by('-pub_date')

class DetailView(generic.DetailView):
	# This file should exist somewhere to render your page
	template_name = 'blogs/detail.html'
	# Should match the value after ':' from url <slug:the_slug>
	slug_url_kwarg = 'the_slug'
	# Should match the name of the slug field on the model 
	slug_field = 'slug' # DetailView's default value: optional
	def get_queryset(self):
		""" Excludes any Posts that aren't published yet."""
		return Post.objects.filter(pub_date__lte=timezone.now())

post_detail_view = DetailView.as_view()

def navbar(request):
	return render(request,'blogs/navbar.html',{'category':Category.objects.filter()})

def home(request):
	if request.user.is_authenticated:
		post = Post.objects.filter(user=request.user).order_by()
	else:
		post = {}
	return render(request,'blogs/home.html',{'posts':post})

def Userregister(request):
	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect("blogs:home")
	else:
		form = RegisterForm()
	return render(request, "blogs/register.html", {"form":form})



def Userlogin(request):
	if request.method == "POST":
		form = LoginForm(request=request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}")
				return redirect('blogs:home')
			else:
				messages.error(request, "Invalid username or password.")
				return HttpResponseRedirect("/login")
		else:
			messages.error(request, "Invalid username or password.")
			return HttpResponseRedirect("/login")
	else:
		form = LoginForm()
		return render(request,'blogs/login.html',{'form':form})



def logout_request(request):
	logout(request)
	messages.info(request, "Logged out successfully!")
	return redirect("/")


def add_post(request):
	if request.method == 'POST':
		form = PostForm(request.POST or None, request.FILES or None)
		if form.is_valid():
			obj = form.save(commit = False) 
			obj.user = request.user; 
			obj.save() 
			form = PostForm() 
			messages.success(request, "Successfully created")
			return redirect('blogs:home')

	return render(request,'blogs/add-post.html',{ 'form':PostForm() })




def delete_post(request):
	post= Post.objects.get(pk=request.POST.get('post_id'))
	if request.method == 'POST':
		post.delete()
		return redirect('blogs:home')
	else:
		messages.error(request,"Something Wrong")


def edit_post(request, id=None, template_name='blogs/edit-post.html'):
    if id:
        post = get_object_or_404(Post, pk=id)
        if post.user != request.user:
            return HttpResponseForbidden()
    else:
        post = Post(user=request.user)

    form = PostForm(request.POST or None, request.FILES or None,instance=post)
    if request.POST and form.is_valid():
        form.save()

        # Save was successful, so redirect to another page
        return redirect('blogs:home')

    return render(request, template_name, {
        'form': form
    })

