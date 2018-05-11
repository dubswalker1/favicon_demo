from django.http import HttpResponse
from django.shortcuts import render

from .forms import FaviconForm
from .models import Favicon
from .services import getFaviconUrl
import pdb

def index(request):
	form = ""
	if request.method == 'POST':
		#pdb.set_trace()
		# try to grab the url value from the request
		url_param = request.POST['url']
		# find any existing model with this url
		instances = Favicon.objects.filter(url=url_param)
		if len(instances) > 0:
			favicon_obj = instances[0]
			# create form using existing instance
			form = FaviconForm(instance=favicon_obj)
			form.fav_url = getFaviconUrl(url_param)
		else:
			# create form using new instance
			form = FaviconForm(data=request.POST)
			form_valid = False
			try:
				form_valid = form.is_valid()
			except ValidationError as e:
				pass
				
			if form_valid:
				data = form.cleaned_data
				url_param = data['url']
				form.fav_url = getFaviconUrl(url_param)
	else:
		form = FaviconForm()
		form.fav_url = None
		# if we are here ... no url to display yet
	return render(request, 'faviconfinder/index.html', {'form': form, 'invalid_url': Favicon.invalid_url()})

