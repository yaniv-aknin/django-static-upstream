django-static-upstream
----------------------

This package probably falls in the "django asset managers" [category](http://djangopackages.com/grids/g/asset-managers/), albeit I'd like to think the reason I'm writing it is that it comes with a twist: rather than assuming you can't serve static assets in production from Python and then working around the rough edges from there, it assumes you will serve your static assets from Python (and work around the rough edges from there).

The core functionality of the package lies in the combination of the {% static %} template tag and the views.serve() view. The former creates links to static assets found in your templates, with hash based versioning. The latter serves them, with apropriate headers and all.

You can read more about the rationale that led me to django-static-upstream [here](http://tech.blog.aknin.name/2011/12/28/i-wish-someone-wrote-django-static-upstream-maybe-even-me/).
