import re
from django import forms
from django.utils.safestring import mark_safe

from .models import Assignment, Story, AssignmentImage

from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

keyword_error_msg = "You must use the name of the animal in your story."
missing_image_msg = "You must select a picture to write about."

class ImageRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
    """
    Custom version of the default RadioField Renderer,
    as django's radio field html is very hard to style.
    """

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        return mark_safe(u'<ul class="inputs-list">\n%s\n</ul>' % 
                u'\n'.join([u'<li class="inputs-image">%s</li>'
                % force_unicode(w) for w in self]))


class AssignmentImageChoiceField(forms.ModelChoiceField):
    """
    Overriding the default ModelChoiceField to generate
    an html image tag from the image, rather than using
    the filename.
    """
    
    def label_from_instance(self, obj):
        image = obj.image.image
        label = """<img src="%s" class="image_select_label" />""" % image.url
        return mark_safe(label)



class StoryForm(forms.ModelForm):
    assignment_image = AssignmentImageChoiceField(queryset=None,
                                              widget=forms.RadioSelect(attrs={'class':'image_selector'}, renderer=ImageRadioFieldRenderer),
                                              empty_label=None,
                                              label='Choose a picture',
                                              error_messages={'required':missing_image_msg, 
                                                              'invalid_choice':missing_image_msg} #this error is obscure and shouldn't happen to most normal users.

                                              )
    
    def __init__(self, *args, **kwargs):
        """
        Filter images that can be used for this story to just
        those associated with the story's assignment.
        """
        assignment = kwargs.pop('assignment')
        super(StoryForm, self).__init__(*args, **kwargs)
        
        assignment_images = AssignmentImage.objects.filter(assignment=assignment)
        self.fields['assignment_image'].queryset = assignment_images
        self.fields['content'].label = "Write a story:"


    def clean_content(self):
        """
        Check the content of the submitted story to ensure it meets
        the requirements for the assignment.
        
        That is, it isn't too long or too short and it contains one of the
        required keywords for the image chosen.
        """
        
        content = self.cleaned_data.get('content', '').strip()
        assignment_image = self.cleaned_data.get('assignment_image', None)
        if assignment_image is None:
            return content #can't perform checks as picture hasn't been chosen; it's okay, though, as that field won't validate.
        
        assignment = assignment_image.assignment

        #length checks
        max_length = assignment.story_max_length
        min_length = assignment.story_min_length
        
        if len(content) < min_length:
            raise forms.ValidationError("Your story must be at least %s characters long." % min_length)
        if len(content) > max_length:
            raise forms.ValidationError("Your story must not be longer than %s characters." % max_length)
        

        #keyword checks
        keywords = assignment_image.keywords

        for keyword in keywords.split(','):
            keyword = keyword.strip()
            
            regex = r'''\b%s\b''' % re.escape(keyword)
            if re.search(regex, content):
                return content
        #if we got here, we didn't find a keyword
        raise forms.ValidationError(keyword_error_msg)
        
        
    class Meta:
        model = Story
        exclude = ('author', 'assignment') #these come from the url and the request