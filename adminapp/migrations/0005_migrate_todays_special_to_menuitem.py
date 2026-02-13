from django.db import migrations

def migrate_todays_special_to_menuitem(apps, schema_editor):
    TodaysSpecial = apps.get_model('adminapp', 'TodaysSpecial')
    MenuItem = apps.get_model('adminapp', 'MenuItem')
    Category = apps.get_model('adminapp', 'Category')
    
    for special in TodaysSpecial.objects.all():
        # Check if a MenuItem with same name and category already exists
        menu_item, created = MenuItem.objects.get_or_create(
            name=special.name,
            category=special.category,
            defaults={
                'image': special.image,
                'rate': special.rate,
                'item_per_plate': special.item_per_plate,
                'is_todays_special': True,
                'special_date': special.date
            }
        )
        
        # If it already exists but wasn't marked as today's special
        if not created and not menu_item.is_todays_special:
            menu_item.is_todays_special = True
            menu_item.special_date = special.date
            menu_item.save()

def reverse_migration(apps, schema_editor):
    # Reverse migration - delete MenuItems created from TodaysSpecial
    MenuItem = apps.get_model('adminapp', 'MenuItem')
    MenuItem.objects.filter(is_todays_special=True).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('adminapp', '0004_menuitem_is_todays_special_menuitem_special_date_and_more'),
    ]

    operations = [
        migrations.RunPython(
            migrate_todays_special_to_menuitem,
            reverse_migration
        ),
    ]