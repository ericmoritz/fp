import fp
import unittest


data = [

    {"host": "app-1",
     "application": "apache",
     "key": "rpm",
     "value": 70},

   {"host": "app-1",
     "application": "apache",
     "key": "rss",
     "value": 115000},

     {"host": "app-1",
      "application": "memcached",
      "key": "objects",
      "value": 1405},

    {"host": "app-1",
     "application": "memcached",
     "key": "rss",
     "value": 245000},

   {"host": "app-2",
     "application": "apache",
     "key": "rpm",
     "value": 3},

    {"host": "app-2",
     "application": "apache",
     "key": "rss",
     "value": 128},

   {"host": "app-2",
     "application": "memcached",
     "key": "objects",
     "value": 100},

    {"host": "app-2",
     "application": "memcached",
     "key": "rss",
     "value": 2048},
]

expected = {
    "app-1": [
        {
            "application": "apache",
            "rpm": 70,
            "rss": 115000,
        },
        {
            "application": "memcached",
            "objects": 1405,
            "rss": 245000,
        },
    ],
    "app-2": [
        {
            "application": "apache",
            "rpm": 3,
            "rss": 128,
        },
        {
            "application": "memcached",
            "objects": 100,
            "rss": 2048,
        },
    ],
}

def collect_stats(stats):
    ret = {}
    seen = {}


    for stat in stats:
        host = stat['host']
        key = stat['key']
        value = stat['value']
        appname = stat['application']

        if host not in ret:
            ret[host] = []
            seen[host] = {}

        if appname not in seen[host]:
            app_dict = {"application": appname}
            ret[host].append(app_dict)
            seen[host][appname] = app_dict
        else:
            app_dict = seen[host][appname]

        app_dict[key] = value

    return ret


class TestCollectStats(unittest.TestCase):

    maxDiff = None
    def test(self):
        self.assertEqual(
            expected,
            collect_stats(data),
        )


from fp import (
    p,
    getter,
    igroupby,
    imap,
    ichain,
    mergedict,
)


group_by_host = p(igroupby, getter("host"))
group_by_app  = p(igroupby, getter("application"))


def reduce_app_group((app, stats)):
    kv = lambda s: (s['key'], s['value'])
    kv_pairs = imap(kv, stats)

    return mergedict(
        {"application": app},
        kv_pairs
    )


class TestReduceAppGroup(unittest.TestCase):
    def test(self):
        self.assertEqual(
            {
                "application": "test",
                "key1": "val1",
                "key2": "val2",
            },
            reduce_app_group(
                (
                    "test",
                    [
                        {"key": "key1", "value": "val1"},
                        {"key": "key2", "value": "val2"},
                    ],
                )
            )
        )


def reduce_host_group((host, stats)):
    return (
        host,
        list(imap(
            reduce_app_group,
            group_by_app(stats)
        ))
    )


class TestReduceHost(unittest.TestCase):
    def test(self):
        self.assertEqual(
            (
                "host",
                [
                    {"application": "app1", "key1": "val1"},
                    {"application": "app2", "key2": "val2"},
                ]
            ),
            reduce_host_group(
                (
                    "host",
                    [
                        {"application": "app1", "key": "key1", "value": "val1"},
                        {"application": "app2", "key": "key2", "value": "val2"},
                    ]
                )
            )
        )


def collect_stats_fp(stats):
    return mergedict(
        {},
        imap(
            reduce_host_group,
            group_by_host(stats)
        )
    )


class TestCollectStatsFP(unittest.TestCase):

    maxDiff = None
    def test(self):
        self.assertEqual(
            expected,
            collect_stats_fp(data),
        )


unittest.main()
