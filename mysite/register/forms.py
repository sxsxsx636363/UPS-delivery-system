from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class UserModificationForm(forms.Form):
    email = forms.EmailField(required=False,widget=forms.TextInput(attrs={'placeholder':'Please enter your new email','class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Please enter your new password','class':'form-control'}), required=False)

class TrackForm(forms.Form):
    tracknum = forms.DecimalField(label="Input tracking number:", min_value=0, max_digits=32, decimal_places=0, widget=forms.TextInput(attrs={'class': 'form-control'}))



class DestForm(forms.Form):
    x = forms.DecimalField(label="x", max_digits=32, decimal_places=0, widget=forms.TextInput(attrs={'class': 'form-control'})) 
    y = forms.DecimalField(label="y", max_digits=32, decimal_places=0, widget=forms.TextInput(attrs={'class': 'form-control'}))
    


class ReportForm(forms.Form):
    email = forms.EmailField(widget=forms.Textarea(attrs={'rows': 1}),required=False, help_text='Enter the email address of the issue reporter.')
    content= forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=False)
 
