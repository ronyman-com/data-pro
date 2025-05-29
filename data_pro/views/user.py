# data_pro/views/user.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

# Import using get_user_model() to avoid AppRegistryNotReady
from django.contrib.auth import get_user_model
User = get_user_model()

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'admin/users/list.html'
    context_object_name = 'users'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    fields = ['username', 'email', 'user_type', 'is_active']
    template_name = 'admin/users/create.html'
    success_url = reverse_lazy('data_pro:user-list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, _('User created successfully'))
        return super().form_valid(form)

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    fields = ['username', 'email', 'user_type', 'is_active']
    template_name = 'admin/users/update.html'
    success_url = reverse_lazy('data_pro:user-list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, _('User updated successfully'))
        return super().form_valid(form)

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'admin/users/delete.html'
    success_url = reverse_lazy('data_pro:user-list')

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('User deleted successfully'))
        return super().delete(request, *args, **kwargs)