from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import redirect


from .forms import FeedbackForm


def feedback_view(request):
    """View to handle user's feedback."""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.send_feedback_email()
            messages.success(request, _('Thank you for your feedback!'))
            return redirect(reverse('onlineshop:home'))
        return render(request, 'feedback/feedback.html', {'form': form})

    if request.user.is_authenticated:
        initial = {'name': request.user.get_full_name(),
                   'email': request.user.email}
        form = FeedbackForm(initial=initial)
    else:
        form = FeedbackForm()
    return render(request, 'feedback/feedback.html', {'form': form})
