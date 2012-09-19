import re
from fp import (
    ap, p, t, first, case, const
)

from itertools import (
    imap, ifilter
)
from operator import eq


def select_view(rules, url):
    matches = ifilter(
        lambda (i, match): match is not None,
        imap(
            lambda (i, (pat, _)): (i, pat.match(url)),
            enumerate(rules)
        )
    )

    try:
        i, match = first(matches)
        pat, view = rules[i]
        return url, match, view
    except StopIteration:
        return None


def apply_view((url, match, view)):
    if url is None:
        return None
    else:
        args = match.groups()
        return view(*args)


def compiled_rules(patterns_to_functions):
    return [
        (re.compile(pat), view)
        for pat, view in patterns_to_functions
    ]


def url_router(*patterns_to_functions):
    # pre-compile the rules
    rules = compiled_rules(patterns_to_functions)

    # return the callable
    return t([
        p(select_view, rules),
        case(
            # If select_view returns None, return None
            (p(eq, None), const(None)),
            # otherwise call apply_view
            (True, apply_view)
        )
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
