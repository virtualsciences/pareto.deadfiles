from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from vs.plonehtml import plonehtml

from .. import deadfiles


class DeadFiles(BrowserView):
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
        processor = plonehtml.PloneHtmlProcessor(
            self._find_linked_uids, True)
        linked_uids = []
        for context, field, uid in processor.process(self.context):
            linked_uids.append(uid)
        deadfiles = deadfiles.find_dead_files(self.context, linked_uids)
        dead = [{
            'uid': item.UID(),
            'url': item.absolute_url(),
            'path': '/'.join(item.getPhysicalPath()),
        } for item in deadfiles]
        # so now we know all UIDs that have a link to them, let's walk
        # through all files to see if their UID is in there
        return {
            'dead': dead,
            'numtotal': len(items),
            'numfixed': len(items) - len(dead),
        }

    def _find_linked_uids(self, html, context):
        # note that this has side-effects not really related to plonehtml's
        # 'find and replace stuff in html' design, it returns a list of uids
        # that are linked to, both from the html and for the object
        return html, deadfiles.find_uids(html, context), False
