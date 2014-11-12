import re

from Products.CMFCore.utils import getToolByName

def related_uids(instance):
    """ find uids that are linked to in the object's relatedItems
    """
    if not hasattr(instance, 'getRelatedItems'):
        return []
    ret = [obj.UID() for obj in instance.getRelatedItems() if obj]
    if ret:
        print 'related items uids:', ret
    return ret

reg_a = re.compile('\shref="resolveuid/([^?#"\/]+)')
reg_nores = re.compile('href="([^"]+)"')
def find_uids(html, context, additional_finders=[related_uids]):
    orghtml = html
    uids = []
    while True:
        match = reg_a.search(html)
        if not match:
            break
        uids.append(match.group(1))
        html = html.replace(match.group(0), '')
    while True:
        match = reg_nores.search(html)
        if not match:
            break
        html = html.replace(match.group(0), '')
    print 'UIDS from html:', uids
    for finder in additional_finders:
        uids += finder(context)
    # always return False to make sure HTML doesn't get overwritten
    return uids

def find_dead_files(
        context, linked_uids, portal_types=('File',), redirector=None):
    catalog = getToolByName(context, 'portal_catalog')
    items = catalog(portal_type=portal_types)
    dead = []
    for item in items:
        # UID is in metadata, so we don't even have to retrieve our
        # objects
        instance = item.getObject()
        path = '/'.join(instance.getPhysicalPath())
        if redirector and redirector.redirects(path):
            print 'found redirect:', path
            #continue
        if item.UID not in linked_uids:
           yield instance
