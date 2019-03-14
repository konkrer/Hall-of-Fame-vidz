from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Hall, Video, SuggestionVideo, User
from .forms import VideoForm, SearchForm
from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from random import choice as randchoice
import urllib
import requests
from .local_data import *

def home(request):
	popular_halls = Hall.objects.all().order_by('-votes_total')[:50]
	return render(request, 'halls/home.html', {'popular_halls': popular_halls})

def newest(request):
	recent_halls = Hall.objects.all().order_by('-id')[:50]
	return render(request, 'halls/home.html', {'recent_halls': recent_halls})

def random(request):
	halls = Hall.objects.all()
	hall_ids = []
	for hall in halls:
		hall_ids.append(hall.id)
	random_id = randchoice(hall_ids)
	return redirect('detail_hall', random_id)


@login_required
def dashboard(request):	
	try:
		halls = Hall.objects.filter(user=request.user)[::-1]
	except TypeError:
		return redirect('login')
	return render(request, 'halls/dashboard.html', {'halls': halls})

@login_required
def add_video(request, pk, suggest):	
	form = VideoForm()
	search_form = SearchForm()
	try:
		hall = Hall.objects.get(pk=pk)
	except NameError:
		return redirect('home')
	if (hall.user != request.user) and (suggest==0):
		raise Http404

	if request.method == 'POST':
		# Create
		form = VideoForm(request.POST)
		if form.is_valid():
			if not suggest:
				video = Video()
			else:
				video = SuggestionVideo()
			video.hall = hall
			video.url = form.cleaned_data['url']
			parsed_url = urllib.parse.urlparse(video.url)
			video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
			if video_id:			 
				video.youtube_id = video_id[0]
				response = requests.get(f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id[0] }&key={YOUTUBE_API_KEY}")
				json = response.json()
				title = json['items'][0]['snippet']['title']
				video.title = title
				thumb_url = json['items'][0]['snippet']['thumbnails']['medium']['url']
				video.thumbnail_url = thumb_url
				video.save()
				return redirect('detail_hall', hall.id)
			else:
				errors = form._errors.setdefault('url', ErrorList())
				errors.append('Needs to be valid Youtube URL')

	return render(request, 'halls/add_video.html', {'form':form, 'search_form':search_form, 'hall': hall, 'suggest': suggest})


@login_required
def add_suggestion_video(request, pk):
	try:
		suggested_video = SuggestionVideo.objects.get(pk=pk)
	except NameError:
		return redirect('home')
	if (suggested_video.hall.user != request.user):
		raise Http404
	video = Video()
	video.hall = suggested_video.hall
	video.title = suggested_video.title
	video.url = suggested_video.url
	video.youtube_id = suggested_video.youtube_id
	video.save()
	SuggestionVideo.objects.filter(id=pk).delete()

	return redirect('dashboard')


@login_required
def video_search(request):
	search_form = SearchForm(request.GET)
	if search_form.is_valid():
		encoded_search_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
		response = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={ encoded_search_term }&key={YOUTUBE_API_KEY}')
		return JsonResponse(response.json())
	return JsonResponse({'error': 'Not able to validate form'})


class DeleteVideo(LoginRequiredMixin, generic.DeleteView):
	model = Video
	template_name = 'halls/delete_video.html'
	success_url = reverse_lazy('dashboard')

	def get_object(self):
		video = super(DeleteVideo, self).get_object()
		if not video.hall.user == self.request.user:
			raise Http404
		return video

class DeleteSuggestionVideo(LoginRequiredMixin, generic.DeleteView):
	model = SuggestionVideo
	template_name = 'halls/delete_video.html'
	success_url = reverse_lazy('dashboard')

	def get_object(self):
		video = super(DeleteSuggestionVideo, self).get_object()
		if not video.hall.user == self.request.user:
			raise Http404
		return video

class SignUp(generic.CreateView):
	form_class = UserCreationForm
	success_url = reverse_lazy('home')
	template_name = 'registration/Signup.html'

	def form_valid(self, form):
		view = super(SignUp, self).form_valid(form)
		username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
		user = authenticate(username=username, password=password)
		login(self.request, user)
		return view

@login_required
def delete_user(request):
	return render(request, 'registration/delete_user.html')

@login_required
def delete_user_confirmed(request, pk):
	if not request.user.id == pk:
		logout(request)
		redirect('home')
	try:
		u = User.objects.get(pk=pk)
		logout(request)
		u.delete()	
		error = 'The user is deleted.'       
	except User.DoesNotExist: 
		error = 'User does not exist.'
	except Exception as e: 
		error = e
	return render(request, 'halls/home.html', {'error': error}) 

class DeleteUserClassy(LoginRequiredMixin, generic.DeleteView):
	model = User
	template_name = 'registration/delete_user.html'
	success_url = reverse_lazy('home')

	def get_object(self):
		user = super(DeleteUserClassy, self).get_object()
		if not user == self.request.user:
			raise Http404
		return user

# CRUD - create read update destroy
class CreateHall(LoginRequiredMixin, generic.CreateView):
	model = Hall
	fields = ['title']
	template_name = 'halls/create_hall.html'
	success_url = reverse_lazy('dashboard')

	def form_valid(self, form):
		form.instance.user = self.request.user
		form.instance.votes = str(self.request.user.id)
		super(CreateHall, self).form_valid(form)
		return redirect('dashboard')

class DetailHall(generic.DetailView):
	model = Hall
	template_name = 'halls/detail_hall.html'

class UpdateHall(LoginRequiredMixin, generic.UpdateView):
	model = Hall
	template_name = 'halls/update_hall.html'
	fields = ['title']
	success_url = reverse_lazy('dashboard')

	def get_object(self):
		model = super(UpdateHall, self).get_object()
		if not model.user == self.request.user:
			raise Http404
		return model

class DeleteHall(LoginRequiredMixin, generic.DeleteView):
	model = Hall
	template_name = 'halls/delete_hall.html'	
	success_url = reverse_lazy('dashboard')

	def get_object(self):
		model = super(DeleteHall, self).get_object()
		if not model.user == self.request.user:
			raise Http404
		return model


@login_required()
def upvote_hall(request, pk):
	if request.method == 'POST':
		hall = get_object_or_404(Hall, pk=pk)
		trying_to_upvote = request.user.id
		lst_upvoted = hall.votes.split(',')
		
		if str(trying_to_upvote) not in lst_upvoted:
			strg = hall.votes + "," + str(trying_to_upvote)
			hall.votes = strg
			hall.votes_total += 1
			hall.save()
		return redirect('detail_hall', hall.id)
	