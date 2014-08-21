from apps.requests.models import RecordType

def populate_record_types():
    rt = RecordType.objects.get_or_create(name='Spreadsheet', description=\
        'Excel or CSV files. Data is organized by rows and columns')
    rt = RecordType.objects.get_or_create(name='GIS/Spatial Information', description=\
        'Shape files (.shp, geojson, xml) containing position and/or outlines of spatial information.')
    rt = RecordType.objects.get_or_create(name='Text documents', description=\
        'Searchable, text-based documents. Generally PDF (non-image based), Word Docs or flat text files.')
    rt = RecordType.objects.get_or_create(name='Emails', description=\
        'All emails concerning a topic, event or including pertinent parties. Information should be produced\
         in a searchable text document if possible.')
