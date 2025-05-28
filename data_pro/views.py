# In data_pro/views.py
from django.shortcuts import render
from django.contrib.auth.views import LoginView


def permission_denied_view(request, exception):
    return render(request, 'admin/403.html', status=403)



class CustomLoginView(LoginView):
    template_name = 'admin/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if not self.request.user.user_type in ['SUPERADMIN', 'CLIENT_ADMIN']:
            messages.error(self.request, "Client admin access required")
            return redirect('system:home')
        return response
    


