import urlparse
import httplib
import subprocess
import libxml2

def check_url(url):
    # a basic check to make sure that the url exists
    p = urlparse.urlparse(url)
    if p[0] != "http":
        raise Exception, "Must use http install URLs"
    if p[1] == "localhost" or p[1] == "localhost.localdomain" or p[1] == "127.0.0.1":
        raise Exception, "Can not use localhost for an install URL"
    conn = httplib.HTTPConnection(p[1])
    conn.request("GET", p[2])
    response = conn.getresponse()
    if response.status != 200:
        raise Exception, "Could not access install url: " + response.reason

def check_iso_install(iso):
    print "Checking ISO...",
    check_url(iso)
    print "OK"

def check_url_install(url):
    print "Checking URL...",
    check_url(url)
    print "OK"

def capture_screenshot(xml, filename):
    doc = libxml2.parseMemory(xml, len(xml))
    graphics = doc.xpathEval('/domain/devices/graphics')
    if len(graphics) != 1:
        print "Failed to find port"
        return
    graphics_type = graphics[0].prop('type')
    port = graphics[0].prop('port')

    if graphics_type != 'vnc':
        print "Graphics type is not VNC, not taking screenshot"
        return

    if port is None:
        print "Port is not specified, not taking screenshot"
        return

    vncport = int(port) - 5900

    vnc = "localhost:" + str(vncport)
    ret = subprocess.call(['gvnccapture', vnc, filename], stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
    if ret != 0:
        print "Failed to take screenshot"
