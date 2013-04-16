from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy

class Assignment(models.Model):
    """
    Represents an image and some logic about assignments
    associated with that image.
    """
    images = models.ManyToManyField('StoryImage', related_name='assignments', through='AssignmentImage')
    name = models.TextField(max_length=32)
    help = models.TextField(max_length=256, help_text='Assignment Details')
    story_max_length = models.IntegerField(default=500) #how many characters can a story for this assignment be?
    story_min_length = models.IntegerField(default=50) #example
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('create_story', kwargs={'assignment':self.pk,})
    
class AssignmentImage(models.Model):
    """
    Represents per-image-per-assignment metadata about an image.
    
    For example, for one assignment users must include the name of the animal in the image.
    In another assignment, users must include something the animal eats or 
    the name for a group of this type of animal.
    """
    image = models.ForeignKey('StoryImage')
    assignment = models.ForeignKey('Assignment')
    keywords = models.TextField(max_length=128) #comma-delimited list of acceptable keywords
    
    def __unicode__(self):
        return u'%s for assignment %s' % (self.image.image, self.assignment.name)

    @property
    def image_url(self):
        return self.image.image.url
    
class StoryImage(models.Model):
    """
    Represents an image that can be used in one or more assignments.
    """    
    image = models.ImageField(upload_to='assignment_images')
    
    def __unicode__(self):
        return self.image
        

class Story(models.Model):
    """
    Represents a story for an assignment.
    """
    assignment = models.ForeignKey(Assignment, related_name='stories')
    assignment_image = models.ForeignKey(AssignmentImage, related_name='image_stories') #the image chosen for this story
    content = models.TextField(max_length=4096) #we might reuse this model to store text beyond 500 chars, don't hardcode that limit here
    author = models.ForeignKey(User)

    @property
    def image_url(self):
        """
        Helper method to retrieve the url for this story.
        """
        return self.assignment_image.image.image.url  #this is gross due to how many related models it goes through

    def get_absolute_url(self):
        return reverse_lazy('view_story', kwargs={'pk':self.pk,})
    

#admin stuff; could be in admin.py
from django.contrib import admin
admin.site.register(Assignment)
admin.site.register(AssignmentImage)
admin.site.register(Story)
admin.site.register(StoryImage)    
