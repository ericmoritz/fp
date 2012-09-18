import re
from fp import ap, p, t, imap, ifirst, ifilter, argfunc


def select_view(rules, url):
    is_match = lambda pat, _: pat.match(url)
    matched_views = ifilter(
        argfunc(is_match),
        rules
    )
    try:
        pat, view = ifirst(matched_views)
        return url, pat, view
    except StopIteration:
        return None, None, None


def apply_view(url, pat, view):
    if url is None:
        return None
    else:
        match = pat.match(url)
        args = match.groups()
        return view(*args)


def compiled_rules(patterns_to_functions):
    compile_route = lambda pat, view: (re.compile(pat), view)

    return map(
        argfunc(compile_route),
        patterns_to_functions
    )


def url_router(*patterns_to_functions):
    # pre-compile the rules
    rules = compiled_rules(patterns_to_functions)

    # return the callable
    return t([
        p(select_view, rules),
        argfunc(apply_view)
    ])


##
# Views
##

def user_view(user_id):
    return "User %s" %(user_id, )


def story_view(story_id):
    return "Story %s" % (story_id, )


def stories_view():
    return "Stories"


if __name__ == '__main__':
    story_routes = url_router(
        (r"^$", stories_view),
        (r"(.+)", story_view)
    )

    route = url_router(
        (r"/stories/([^/]*)", story_routes),
        (r"/users/([^/]+)/", user_view),
    )

    print "%r" % (route("/stories/"), )
    print "%r" % (route("/stories/10/"), )
    print "%r" % (route("/users/10/"), )
