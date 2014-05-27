# Handkerchief - a trivial offline issue reader for GitHub Issues

This script allows you to easily download the open issues of a GitHub
Repository and store them in a single easily browsable, standalone html file.

## The name

I chose the name, because the obvious pun name "tissues" was already taken. It
also fits, because being offline is somewhat oldfashioned, just like the word
handkerchief.

## Getting Started

Clone the repository anywhere onto your machine and just call the script with the user or organisation and repository name

    handkerchief.py jreinhardt/tissues
		
If you are on a mac you can optionally add the following to your ~/.bash_profile.

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
	
Now you can run `handkerchief jreinhardt/tissues` or if you are within the repository just `handkerchief`.

## Dependencies

Requires [Python 2.7](http://www.python.org) and the [requests library](http://www.python-requests.org/).

Installing dependencies:

```bash
	# using homebrew
	brew install python
	# using pip
	pip install requests
````

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

