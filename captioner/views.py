from django.views.generic.edit import CreateView

from .models import Assignment, Story
from .forms import StoryForm
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView

class CreateStory(CreateView):
    model = Story
    form_class = StoryForm

    def get_form_kwargs(self):
        """
        Provide the assignment from the url to the form.
        """
        kwargs = CreateView.get_form_kwargs(self)
        kwargs['assignment'] = get_object_or_404(Assignment, pk=self.kwargs.get('assignment'))
        return kwargs
    
    
    def form_valid(self, form):
        """
        Handles the bulk of story validation.
        Also associates the Story with the current
        logged-in user and the assignment from the url.
        """
        
        form.instance.author = self.request.user
        form.instance.assignment = get_object_or_404(Assignment, pk=self.kwargs.get('assignment'))
        
        return super(CreateStory, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = CreateView.get_context_data(self, **kwargs)
        context['assignment'] = get_object_or_404(Assignment, pk=self.kwargs['assignment'])
        return context
        
class ViewStory(DetailView):
    model = Story