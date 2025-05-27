import pandas as pd
from django.db import transaction
from io import BytesIO
from datetime import datetime

class ExcelImporter:
    def __init__(self, model_class, user):
        self.model_class = model_class
        self.user = user
    
    @transaction.atomic
    def import_from_excel(self, file):
        df = pd.read_excel(file)
        created_objects = []
        
        for _, row in df.iterrows():
            data = self.prepare_data(row.to_dict())
            obj = self.model_class(**data)
            obj.created_by = self.user
            obj.updated_by = self.user
            obj.save()
            created_objects.append(obj)
        
        return created_objects
    
    def prepare_data(self, row_data):
        # Convert date strings to date objects
        date_fields = [f.name for f in self.model_class._meta.get_fields() 
                      if f.get_internal_type() == 'DateField']
        
        for field in date_fields:
            if field in row_data and pd.notna(row_data[field]):
                if isinstance(row_data[field], str):
                    row_data[field] = datetime.strptime(row_data[field], '%Y-%m-%d').date()
                elif pd.is_datetime64_any_dtype(row_data[field]):
                    row_data[field] = row_data[field].to_pydatetime().date()
        
        # Handle foreign keys
        fk_fields = [f for f in self.model_class._meta.get_fields() 
                    if f.is_relation and f.many_to_one and not f.auto_created]
        
        for field in fk_fields:
            if field.name in row_data and pd.notna(row_data[field.name]):
                related_model = field.related_model
                if isinstance(row_data[field.name], (int, str)):
                    try:
                        row_data[field.name] = related_model.objects.get(pk=row_data[field.name])
                    except related_model.DoesNotExist:
                        row_data[field.name] = None
        
        return row_data

class ExcelExporter:
    @staticmethod
    def export_to_excel(queryset, fields=None):
        if fields is None:
            fields = [f.name for f in queryset.model._meta.get_fields() 
                     if not f.is_relation or f.many_to_one and not f.auto_created]
        
        data = []
        for obj in queryset:
            row = {}
            for field in fields:
                value = getattr(obj, field)
                if hasattr(value, 'isoformat'):  # Handle date/datetime
                    value = value.isoformat()
                elif hasattr(value, 'pk'):  # Handle foreign keys
                    value = value.pk
                row[field] = value
            data.append(row)
        
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return output