#!/usr/bin/python 

import urllib2, re, urlparse, sys, os, tempfile, logging
# regex for image links
regex = re.compile("http\://[^:]+\.jpg")
# if http://www.servimg.com/image_preview.php?i=010&u=12345678 is address
# of one image, then user_id is 12345678
user_id = "13556200"
# allowed_empty_streak is maximum number of successive links without image
# if have been found more than allowed_empty_streak links without image
# program will no longer search for images
allowed_empty_streak = 5


def download_file(url):
    u = urllib2.urlopen(url)
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)
    if not filename:
        filename = 'no_name_file'
    with open(filename, 'wb') as f:
        meta = u.info()
        meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
        meta_length = meta_func("Content-Length")
        file_size = None
        if meta_length:
            file_size = int(meta_length[0])
        actual_size = 0
        while True:
            buffer = u.read(8192)
            if not buffer:
                break
            actual_size += len(buffer)
            f.write(buffer)
    return filename

# get user_id from script arguments
if (len(sys.argv) <= 1 ):
	print "This program takes one argument: servimg.com user_id."
	print "Exiting..."
	exit()
reuserid = re.compile("\d{8}")
reobjuser = reuserid.match(sys.argv[1])
if reobjuser == None:
	print "Provided user_id is not well formated."
	exit()
else:
	user_id = reobjuser.group(0)

no_of_discovered_links = 0
empty_streak = 0
try:
	for i in range(1, 999):
		if empty_streak >= allowed_empty_streak:
			break
		k = str(i).zfill(3)
		url = 'http://www.servimg.com/image_preview.php?i=' + str(k) + '&u=' + user_id
		response = urllib2.urlopen(url)
		# check if page is redirected
		if (response.geturl() == url):
			# check if page is redirected
			if (response.getcode() != 200):
				print "Page cannot be opened.Error streak = " + str(empty_streak)
				empty_streak += 1
				continue
			else:
				html = response.read()
				# eventually I should look others links than just first one
				link_re = regex.search(html)
				if (link_re == None):
					empty_streak += 1
					continue
				empty_streak = 0
				link = link_re.group(0)
				fn = download_file(link)
				print fn + " downloaded."
				no_of_discovered_links += 1

		else:
			empty_streak += 1
			print "Unexpected behavior: page is redirected. Error streak = " + str(empty_streak)
			continue

		response.close()
	print "Downloaded " + str(no_of_discovered_links) + " files."
except urllib2.URLError, e:
	print "Error: Connection problem. Check Your network settings."