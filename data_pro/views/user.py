# data_pro/views/user.py
from django.contrib.auth import get_user_model
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from data_pro.forms.user import UserForm

User = get_user_model()

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'admin/user/list.html'
    context_object_name = 'users'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return super().get_queryset().select_related('client_profile')

class UserCreateView(CreateView):
    model = User
    form_class = UserCreateForm  # Use the creation form
    template_name = 'admin/user/create.html'
    success_url = reverse_lazy('data_pro:user-list')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm  # Use the update form
    template_name = 'admin/user/update.html'
    success_url = reverse_lazy('data_pro:user-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'admin/user/delete.html'
    success_url = reverse_lazy('data_pro:user-list')

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"User {self.object.username} deleted successfully")
        return response