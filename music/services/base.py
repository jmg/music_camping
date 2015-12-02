# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from shopify_app.utils.render import render, render_string
from shopify_app.utils.python import convert_to_bool
from django.http import HttpResponse
import json
from django.utils.cache import add_never_cache_headers
from django.db.models import Q
from music.utils.query_parser import parse


class BaseService(object):

    _repo = property(fget=lambda self: self.entity.objects)
    _page_size = 10

    default_query_params = {}

    def __getattr__(self, name):
        """
            Delegates automatically all undefined methods on the repository entity.
        """

        def decorator(*args, **kwargs):

            method = getattr(self._repo, name)
            if method is None:
                raise AttributeError("'%s' has no attribute '%s'" % (self.__class__.__name__, name))

            if not kwargs.pop("without_filters", False):
                for key, value in self.default_query_params.iteritems():
                    kwargs.setdefault(key, value)

            return method(*args, **kwargs)

        return decorator

    def get_page(self, page=0, size=None, min_page=None, **kwargs):

        if size is None:
            size = self._page_size

        page = int(page)

        if min_page is not None:
            min_page = int(min_page)
            limit = (page + 1) * size
            offset = min_page * size
        else:
            limit = (page + 1) * size
            offset = size * page

        return self._get_objects(self._get_page_query(offset, limit, **kwargs))

    def _get_page_query(self, offset, limit, **kwargs):

        return self.all()[offset:limit]

    def list(self, start, size, **kwargs):
        page = int(start / size)
        return self.get_page(page=page, size=size, min_page=None, **kwargs)

    def _get_objects(self, objects):
        """ Override to add behaviour """

        return objects

    def get_one(self, *args, **kwargs):

        objects = self.filter(*args, **kwargs)
        return objects[0] if objects else None

    def new(self, *args, **kwargs):

        return self.entity(*args, **kwargs)

    def _get_or_new(self, *args, **kwargs):

        try:
            obj, created = self.get_or_create(*args, **kwargs)
        except:
            obj, created = self.entity(*args, **kwargs), True
        return obj, created

    def get_or_new(self, *args, **kwargs):

        obj, _ = self._get_or_new(*args, **kwargs)
        return obj

    def update_or_create(self, pre_create_function=None, pre_update_function=None, *args, **kwargs):

        entity_id = kwargs.pop("id", None)
        if entity_id:

            if pre_update_function is not None:
                pre_update_function(kwargs)

            entity = self.get(id=entity_id)
            for key, value in kwargs.iteritems():
                setattr(entity, key, value)

        else:
            if pre_create_function is not None:
                pre_create_function(kwargs)

            entity = self.new(**kwargs)

        entity.save()
        return entity

    def get_or_new_created(self, *args, **kwargs):

        return self._get_or_new(*args, **kwargs)

    def get_form(self):

        return None

    def _get_data(self, request, *args, **kwargs):
        instance = self.entity()
        data = dict([(key, value) for key, value in request.POST.iteritems() if key != "csrfmiddlewaretoken" and hasattr(instance, key)])
        data.update(self._get_additional_data(request))
        return data

    def _get_additional_data(self, request, *args, **kwargs):

        return {}

    def _get_entity(self, request, *args, **kwargs):

        return self.get_or_new(**self._get_data(request))

    def _set_data(self, entity, request, *args, **kwargs):

        data = self._get_data(request)
        for key, value in data.iteritems():
            setattr(entity, key, value)
        return entity

    def set_attrs(self, entity, attrs):

        for key, value in attrs.iteritems():
            setattr(entity, key, value)

    def save_entity(self, entity, *args, **kwargs):

        entity.save()

    def save(self, request, *args, **kwargs):

        entity = self._get_entity(request, *args, **kwargs)

        self._set_data(entity, request, *args, **kwargs)
        self.save_entity(entity, *args, **kwargs)
        self._post_save(entity, request, *args, **kwargs)

        return entity

    def _post_save(self, entity, request, *args, **kwargs):

        pass

    def render(self, template, context):

        return render(template, context)

    def render_string(self, string, context):

        return render_string(string, context)

    def get_object_or_404(self, **kwargs):

        return get_object_or_404(self.entity, **kwargs)

    def delete(self, *args, **kwargs):

        logical_delete = kwargs.pop("logical", False)

        objs = self.filter(*args, **kwargs)

        if not objs:
            return False

        for obj in objs:
            if not logical_delete:
                obj.delete()
            else:
                obj.active = False
                obj.save()

        return True

    def get_formated_sum(self, value):

        if value is None:
            value = 0

        return "%.2f" % value

    def _render_row_value(self, row_data, render):

        if isinstance(render, basestring):
            if isinstance(row_data, dict):
                return unicode(row_data[render])
            else:
                return unicode(getattr(row_data, render))
        else:
            return unicode(render(row_data))

    def get_params(self, data, params):

        dict_params = {}
        for param in params:
            dict_params[param] = data.get(param)
        return dict_params

    def convert_to_bool(self, data, params):

        convert_to_bool(data, params)

    def to_bool(self, param):

        return bool(int(param))

    def get_action_params(self, request, params_names, prefix="", bar_action=True):

        complete_names = ["%s%s" % (prefix, param) for param in params_names]

        params = self.get_params(request.POST, complete_names)

        if bar_action:
            boolean_params = ["%s%s" % (prefix, param) for param in ["is_main_action", "is_side_action"]]
            self.convert_to_bool(params, boolean_params)

        final_params = {}
        for key, value in params.iteritems():
            new_key = key.replace(prefix, "")
            final_params[new_key] = value

        return final_params

    def check_nullables(self, data, params):

        for param in params:
            if not data.get(param):
                data[param] = None

    def open_search(self, request, columnIndexNameMap, columnSortIndexNameMap, extra_response_params={}, qs=None, *args, **kwargs):

        open_search_data = parse(request.META["QUERY_STRING"])
        sort_prop_name = None
        if "iSortCol_0" in open_search_data and columnSortIndexNameMap[int(open_search_data['iSortCol_0'])]:
            sort_prop_name = columnSortIndexNameMap[int(open_search_data['iSortCol_0'])] # Sort column
            if open_search_data['sSortDir_0'] == "desc":
                sort_prop_name = "-%s" % sort_prop_name

        if qs is None:
            if sort_prop_name:
                querySet = self.filter(*args, **kwargs).order_by(sort_prop_name)
            else:
                querySet = self.filter(*args, **kwargs)
        else:
            querySet = qs.filter(*args, **kwargs)

        cols = int(len(columnIndexNameMap)) # Get the number of columns
        iDisplayLength =  min(int(open_search_data.get('length',10)),100)     #Safety measure. If someone messes with iDisplayLength manually, we clip it to the max value of 100.
        startRecord = int(open_search_data.get('start',0)) # Where the data starts from (page)
        endRecord = startRecord + iDisplayLength  # where the data ends (end of page)

        # Determine which columns are searchable
        searchableColumns = []
        for col, data in open_search_data["columns"].items():
            if data["searchable"] == 'true':
                if not data["search"].get("value"):
                    searchableColumns.append(columnIndexNameMap[col])
                else:
                    searchableColumns = searchableColumns + data["search"].get("value").split(",")

        print searchableColumns

        # Apply filtering by value sent by user
        customSearch = open_search_data["search"].get('value', '').encode('utf-8');
        if customSearch != '':
            outputQ = None
            first = True
            for searchableColumn in searchableColumns:
                kwargz = {searchableColumn+"__icontains" : customSearch}
                outputQ = outputQ | Q(**kwargz) if outputQ else Q(**kwargz)
            querySet = querySet.filter(outputQ)

        sEcho = int(open_search_data.get('sEcho',0)) # required echo response

        iTotalRecords = iTotalDisplayRecords = querySet.count() #count how many records match the final criteria
        querySet = querySet[startRecord:endRecord] #get the slice

        keys = columnIndexNameMap.keys()
        keys.sort()
        colitems = [columnIndexNameMap[key] for key in keys]
        sColumns = ",".join(map(str,colitems))

        aaData = []
        for row in querySet :
            rowlist = []
            [ rowlist.append( self._render_row_value(row, col) )  for col in colitems ]
            aaData.append(rowlist)

        response_dict = {}
        response_dict.update({'aaData':aaData})
        response_dict.update(extra_response_params)

        response_dict.update({'sEcho': sEcho, 'iTotalRecords': iTotalRecords, 'iTotalDisplayRecords':iTotalDisplayRecords, 'sColumns':sColumns})
        response = HttpResponse(json.dumps(response_dict))
        response["Content-type"] = 'application/json'

        #prevent from caching datatables result
        add_never_cache_headers(response)
        return response

    def _render_row_value(self, row_data, render):

        if isinstance(render, basestring):
            if isinstance(row_data, dict):
                return unicode(row_data[render])
            else:
                return unicode(getattr(row_data, render))
        else:
            return unicode(render(row_data))
