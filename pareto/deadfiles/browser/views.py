import re

from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from pareto.plonehtml import plonehtml


class DeadFiles(BrowserView):
    portal_types = ('File',)
    template = ViewPageTemplateFile('deadfiles.pt')

    def __call__(self):
        if self.request.get('remove-submit'):
            toremove = self.request.getlist('remove')
            for path in toremove:
                path = path.split('/')
                parent = self.context.restrictedTraverse(path[:-1])
                parent.manage_delObjects([path[-1]])
        return self.template()

    def results(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        processor = plonehtml.PloneHtmlProcessor(self._find_linked_uids, True)
        linked_uids = []
        for context, field, uid in processor.process(self.context):
            linked_uids.append(uid)
        # so now we know all UIDs that have a link to them, let's walk through
        # all files to see if their UID is in there
        catalog = getToolByName(self.context, 'portal_catalog')
        items = catalog(portal_type=self.portal_types)
        dead = []
        for item in items:
            # UID is in metadata, so we don't even have to retrieve our objects
            if item.UID not in linked_uids:
                instance = item.getObject()
                dead.append({
                    'uid': item.UID,
                    'url': instance.absolute_url(),
                    'path': '/'.join(instance.getPhysicalPath())})
        return {
            'dead': dead,
            'numtotal': len(items),
            'numfixed': len(items) - len(dead),
        }

    reg_a = re.compile('\shref="resolveuid/([^?#"\/]+)')
    reg_nores = re.compile('href="([^"]+)"')
    def _find_linked_uids(self, html, context):
        orghtml = html
        uids = []
        while True:
            match = self.reg_a.search(html)
            if not match:
                break
            uids.append(match.group(1))
            html = html.replace(match.group(0), '')
        while True:
            match = self.reg_nores.search(html)
            if not match:
                break
            html = html.replace(match.group(0), '')
        # always return False to make sure HTML doesn't get overwritten
        return html, uids, False
