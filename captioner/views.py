from django.views.generic.edit import CreateView

from .models import Assignment, Story
from .forms import StoryForm
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView

class CreateStory(CreateView):
    """
    Basic story submission view; handles displaying the story form and 
    template variables.
    """
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
        Provides author (logged-in user) and assignment (from url)
        data to the StoryForm instance.
        """
        form.instance.author = self.request.user
        form.instance.assignment = get_object_or_404(Assignment, pk=self.kwargs.get('assignment'))
        return super(CreateStory, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Provides the current page's assignment to the template context,
        to allow displaying the assignment's name and help text.
        """
        context = CreateView.get_context_data(self, **kwargs)
        context['assignment'] = get_object_or_404(Assignment, pk=self.kwargs['assignment'])
        return context
        
class ViewStory(DetailView):
    """
    Extremely simple view to display a story after it's been submitted.
    """
    model = Story