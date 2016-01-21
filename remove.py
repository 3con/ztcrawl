import redis
import sys

REDIS_HOST = "10.171.211.84"
REDIS_PORT = 6379
REDIS_PASS = 'ztolredis'
# r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT,password=REDIS_PASS)
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

if len(sys.argv) > 1:
    l = r.keys("Crawl_%s_*" % (sys.argv[1],))
    r.delete(*tuple(l))
else:
    l = r.keys("Crawl_*")
    r.delete(*tuple(l))