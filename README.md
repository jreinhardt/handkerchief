# Handkerchief - a simple offline issue reader for GitHub Issues

This script allows you to easily download the open issues of a GitHub
Repository and store them in a offline browsable, single standalone html file.

## The name

I chose the name, because the obvious pun name "tissues" was already taken. It
also fits, because being offline is somewhat oldfashioned, just like the word
handkerchief.

## Getting Started

Clone the repository anywhere onto your machine and just call the script with
the user or organisation and repository name

    handkerchief.py jreinhardt/tissues

If you are on a mac you can optionally add the following to your
~/.bash_profile.

```bash
function handkerchief {
  # change this path to the location of handkerchief.py
  hand=~/handkerchief/handkerchief.py
  if [[ $1 != "" ]] ; then
    python $hand $1
	else
    repo=$(git remote -v | head -n1 | awk '{print $2}' | sed -e 's,.*:\(.*/\)\?,,' -e 's/\.git$//')
    if [[ $repo == *https://* ]] ; then
      python $hand ${repo#https://github.com/}
    elif [[ $repo == *git@github.com* ]] ; then
      python $hand ${repo#git@github.com:}
    else
      echo "Provide parameter"
    fi
  fi
}
```
	
Now you can run `handkerchief jreinhardt/handkerchief` or if you are within the
repository just `handkerchief`.

There are a few options available, for details see `handkerchief --help`.

## Dependencies

Requires [Python 2.7](http://www.python.org), the
[Jinja2 template system](http://jinja.pocoo.org/)  and the
[requests library](http://www.python-requests.org/).

For most Linux distributions, these should be available via the package
manager. On MacOS you can install the dependencies by:

```bash
# using homebrew
brew install python
# using pip
pip install requests
pip install Jinja2
````

For Windows there is an installer for Python available from the [Python
Website](http://www.python.org/downloads), and the rest can be installed via
pip:

```bash
pip install requests
pip install Jinja2
````

## Layouts

Handkerchief offers a simple way to modify the visual appearance and
functionality of the resulting offline html file, by changing to a different layout.

A layout consists of a parameter and a template file, and a number of
javascript and css files, which reside in a subfolder of the layouts folder in
the handkerchief repository. To produce the output file, the template file gets
populated with the data, and the javascript and css files are inlined. If not
told otherwise, handkerchief will fetch layouts from the handkerchief GitHub
repository, so that always the most up to date version of the layout is used.

The parameter file is a json file with the same name as the subfolder in which
it resides. It contains an associative array with three keys:

* html: the file name of the template file
* css: a list of filenames of stylesheets to inline
* js: a list of filenames of javascript files to inline

The template is processed by [Jinja2](http://jinja.pocoo.org/), and the
following variables are available:

* repo: a dictionary containing information about the repository, see
  [GitHub API docs](https://developer.github.com/v3/repos/)
* issues: a list of dictionaries containing issue data, see 
  [GitHub API docs](https://developer.github.com/v3/issues/). Each issue has an
  additional field 'comments_list' with a list of all comments (see 
  [GitHub API docs](https://developer.github.com/v3/issues/comments)) for this
  issue. The comment data is augmented by a string in
  `comment['user']['avatar_class']` which contains a css class that sets the
  avatar of the user as background image of the element.
* labels: a list of dictionaries containing label data, see
  [GitHub API docs](https://developer.github.com/v3/issues/labels)
* milestones: a list of dictionaries containing milestone data, see
  [GitHub API docs](https://developer.github.com/v3/issues/milestones)
* javascript: a dictionary with the names of the javascript files as keys, and
  their contents as values. Additionally it contains a stylesheet that defines
  classes of the form `avatar_username` that set the avatar of a user as
  background image of an element.
* stylesheets: a list with the contents of the stylesheets

If you have created a new layout or improved a existing one, feel free to open
a pull request, contributions are always welcome!

## License

Handkerchief is licensed under the [MIT license](http://opensource.org/licenses/MIT)

    The MIT License (MIT)

    Copyright (c) 2013 Johannes Reinhardt <jreinhardt@ist-dein-freund.de>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

