from django.contrib import admin
from django.db import transaction
from .models import Favicon
from .services import getFaviconUrl
import pdb
import requests, zipfile, io

class FaviconAdmin(admin.ModelAdmin):
    list_display = ('url', 'fav_url', 'created')
admin.site.register(Favicon, FaviconAdmin)

# Register your models here.
# avoid concurrency issues
@ transaction.atomic
def seed_db(ModelAdmin, request, queryset):
	#pdb.set_trace()
	# seed the database via zip download
	# remove all entries in DB (otherwise we'd need to worry about duplicate URLs
	Favicon.objects.select_for_update().all().delete()
	# request the zip
	try:
		zip_file_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
		response = requests.get(zip_file_url, timeout=1.0)
		response.raise_for_status()
	except  requests.exceptions.RequestException as e:
		admin.ModelAdmin.message_user(request, e) 
	else:
		if response.ok:
			z = zipfile.ZipFile(io.BytesIO(response.content))
			member_names = z.namelist()
			info = z.getinfo(member_names[0])
			bytes_obj = z.open(member_names[0])
			byte_str = bytes_obj.read()
			text_obj = byte_str.decode('UTF-8')
			string_obj = io.StringIO(text_obj)
			entries = []
			start_at = 160000
			stop_at = 199900
			for i in range(200000):
				url = string_obj.readline().split(",")[1].strip()
				if i > start_at and i < stop_at:
					entries.append(url)
					obj = Favicon()
					obj.url = "http://www."+url
					#this call should take care of saving
					obj.fav_url = getFaviconUrl(obj.url)
				
			print("num_entries:"+str(len(entries)))
			
			
seed_db.short_description = "Refresh the database and seed"

admin.site.add_action(seed_db, "seed_db")