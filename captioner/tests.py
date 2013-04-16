"""
Tests for the captioner app.

@todo: test the actual views.  These tests focus mainly on form validation.
"""

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Assignment, AssignmentImage, StoryImage
from .forms import StoryForm, keyword_error_msg
from django.db.utils import IntegrityError
from captioner.forms import missing_image_msg

class AssignmentFormTests(TestCase):
    """
    Simple tests of submitting the assignment form.
    Most of the heavy validation lifting is done in the form,
    so this is where I'm concentrating on testing.
    """
    
    def setUp(self):
        """
        Basic fixtures:  an assignment, three images, and m2m relationships.
        Also a user.
        """
        self.assignment = Assignment.objects.create(name='Test Assignment',
                                     help="Test help",
                                     story_min_length=1,
                                     story_max_length=500)

        #make some images and associate them with the assignment.
        self.images = []
        for i in range(3):
            story_image = StoryImage.objects.create(image='test_image_%s.jpg' % i)
            AssignmentImage.objects.create(image=story_image,
                                           assignment=self.assignment,
                                           keywords="test, testing",
                                           )
            self.images.append(story_image)

        self.image = self.images[0]
        self.assignment_image = self.image.assignmentimage_set.all()[0]
        self.user = User.objects.create_user(username='test_user', email='test@test.com', password='test_pass')

    def test_form_bad_keywords(self):
        """
        Test to ensure that the form correctly checks for presence of keywords
        in the story.
        """
        bad_form_data = {'assignment_image': self.assignment_image.pk,
                         'content': "Not a very good story"} #doesn't contain keywords
        form = StoryForm(data=bad_form_data, assignment=self.assignment)

        self.assertFalse(form.is_valid())
        content_error = form.errors['content']
        self.assertEqual(content_error[0], keyword_error_msg)
        
    def test_form_good_and_save(self):
        """
        Simple test of an ideal condition, to ensure the user/assignment 
        logic works and is saved with the resulting Story object.
        """
        form_data = {'assignment_image': self.assignment_image.pk,
                     'content': "A good story about testing."} #doesn't contain keywords

        form = StoryForm(data=form_data, assignment=self.assignment)
        self.assertTrue(form.is_valid())

        #while the form is valid, the Story object isn't, as it has no author or assignment.
        self.assertRaises(IntegrityError, form.save)

        #mimic the responsibilities of the view
        form.instance.author = self.user
        form.instance.assignment = self.assignment
        res = form.save()

        self.assertEqual(res.content, form_data['content'])
        self.assertEqual(res.author, self.user)
        self.assertEqual(res.assignment, self.assignment)
        self.assertEqual(res.assignment_image, self.assignment_image)

    def test_form_display(self):
        """
        The main things we care about:
        can't select a user, can't select an assignment (those are from the page/request)
        and images(s) display.
        """
        
        form = StoryForm(assignment=self.assignment)
        form_html = form.as_p()
        
        self.assertFalse('user' in form_html)
        self.assertFalse('Test Assignment' in form_html)
        for story_image in self.assignment.images.all():
            self.assertTrue(story_image.image.url in form_html)
        
    def test_form_excludes_other_images(self):
        """
        Images can be assigned to more than one assignment
        and assignments can have more than one image.
        Ensure that the form only displays images for the assignment in question.
        """
        other_image = StoryImage.objects.create(image='not_this_one.jpg')
        other_assignment = Assignment.objects.create(name='Other Assignment')

        #and relate the image to the assignment
        other_assignment_image = AssignmentImage.objects.create(image=other_image, 
                                                                assignment=other_assignment, 
                                                                keywords='wrong assignment')
        #ensure the form doesn't show images from the wrong assignment.
        form = StoryForm(assignment=self.assignment)
        self.assertFalse(other_image.image.url in form.as_p())

        #ensure the form doesn't let you pick images from the wrong assignment.
        bad_form_data = {'assignment_image': other_assignment_image.pk,
                         'content': "Not a very good story"} #doesn't contain keywords
        form = StoryForm(assignment=self.assignment, data=bad_form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['assignment_image'][0], missing_image_msg)
