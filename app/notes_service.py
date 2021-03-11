from .models import *
import datetime
import os
import datetime


class NotesService:

    def get_all_notes(self, login, filter):
        """Returns list of dicts with notes for specific user"""
        output = []

        if filter["category"] == [None]:
            filter["category"] = Categories.objects.all()

        all_records = Journal.objects.filter(
            login=login,
            date__range=(filter["startdate"], filter["stopdate"]),
            category__in=filter["category"],
        ).order_by("date")
        for item in all_records:
            attachments = Attachment.objects.filter(journal_id=item.id).order_by("date")
            output.append(
                {
                    "id": item.id,
                    "login": item.login.username,  # related object
                    "date": item.date.strftime("%d-%m-%Y"),
                    "value": item.value,
                    "category": item.category.category,  # related object
                    "description": item.description,
                    "attachments": attachments,
                }
            )
        return output

    def page_values_sum(self, notes):
        """Counts summary for specific notes from def "show_notes" """
        value_sum = sum([item.get("value") for item in notes])
        return value_sum

    def set_filter(self, request):
        """Set filter with default category and dates, to display notes"""
        filter = {
            "startdate": datetime.date.today() - datetime.timedelta(days=365),
            "stopdate": datetime.date.today(),
            "category": [None],
        }

        # change filter category to user default if user has it
        if request.user.profile.default_category:  
            default_category = Categories.objects.get(
                login=request.user.id, id=request.user.profile.default_category.id
            )
            filter.update({"category": [default_category,]})

        # if filter was NOT set today - dont read any further
        if str(request.session.get("setdate")) < str(datetime.date.today()):
            return filter

        # change filter to last choices from cookies, if it exist
        if request.session.get("category") not in [[None], None,]:
            category_id = Categories.objects.get(id=request.session["category"][0])
            filter.update(
                {
                    "category": [category_id],
                    "startdate": request.session.get("startdate"),
                    "stopdate": request.session.get("stopdate"),
                })
        return filter

    def save_attachments(self, request, note):
        """Moves files from temp to folder to specific note folder,
           after the note is saved
        """
        user_path = os.path.join('media', 'attachments', f'{request.user.id}')
        user_temp_path = os.path.join('media', 'attachments', f'{request.user.id}', 'temp')
        if not os.path.exists(user_temp_path):
            return []
        os.makedirs(os.path.join('media', 'attachments', f'{request.user.id}', 'temp'), exist_ok=True)
        file_names = os.listdir(f'media/attachments/{request.user.id}/temp')
        attachments = []
        for file_name in file_names:
            source_path = os.path.join(user_path, 'temp', file_name)
            dest_path = os.path.join(user_path, f'{note.id}', file_name)
            if not os.path.exists(os.path.join(user_path, f'{note.id}')):
                os.makedirs(os.path.join(user_path, f'{note.id}'))
            os.rename(source_path , dest_path)
            attachment = Attachment(
                journal_id=note,
                date=datetime.date.today(),
                login=request.user,
                description='',
                file=os.path.join('attachments', f'{request.user.id}', f'{note.id}', file_name),
                file_name=file_name,
            )
            attachment.save()
            attachments.append(attachment)
        return attachments