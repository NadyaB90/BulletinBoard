from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from .filter import CommentFilter
from .forms import CommentForm
from .models import Bulletin, Comment, CategoryModel
from django.urls import reverse_lazy
import django.dispatch
from django.contrib.auth.decorators import login_required


def home(request):
    context = {
        'bulletins': Bulletin.objects.all()
    }
    return render(request, 'board/home.html', context)


class PostListView(ListView):
    model = Bulletin
    template_name = 'board/home.html'
    context_object_name = 'bulletins_'
    ordering = ['-date_created']
    paginate_by = 2


class UserPostListView(ListView):
    model = Bulletin
    template_name = 'board/user_posts.html'
    context_object_name = 'bulletins_'
    ordering = ['-date_created']
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Bulletin.objects.filter(author=user).order_by('-date_created')


class PostDetailView(DetailView):
    model = Bulletin


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Bulletin
    fields = ['title', 'content', 'bulletin_category', 'file']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('home')


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.bulletin_id = self.kwargs['pk']
        form.instance.username = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('home')


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Bulletin
    fields = ['title', 'content', 'bulletin_category']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        bulletin = self.get_object()
        if self.request.user == bulletin.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bulletin
    success_url = '/home'

    def test_func(self):
        bulletin = self.get_object()
        if self.request.user == bulletin.author:
            return True
        return False


class CommentListView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'board/comment_list.html'
    context_object_name = 'comments'
    ordering = ['-date_added']
    paginate_by = 3
    myFilter = CommentFilter()

    def get_queryset(self):
        user_id = self.request.user.id
        return Comment.objects.filter(bulletin__author_id=user_id).order_by('-date_added')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['filter'] = CommentFilter(self.request.GET, queryset=self.get_queryset())

        return context


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    success_url = reverse_lazy('comment_list')


accepted = django.dispatch.Signal()


def accept(request, **kwargs):

    accepted.send(sender=Comment.__class__, **kwargs)

    return redirect('/home/comments')


@login_required
def subscribe(request, **kwargs):
    print(kwargs['pk'])
    pk = kwargs['pk']
    my_post = Bulletin.objects.get(id=pk).bulletin_category
    print(my_post)

    CategoryModel.objects.get(id=my_post.id).subscribers.add(request.user)

    subscribers = CategoryModel.objects.filter(subscribers=request.user)
    print(f"subscribed categories={subscribers.values()}")
    print('Эта новость относится к категории:', subscribers.last())
    print(subscribers)
    print('Вы подписаны на следующие категории: ', end='')
    for i in Bulletin.objects.filter(bulletin_category__subscribers=request.user.id):
        print(i, end='    ')
    print("")
    return redirect('/')
