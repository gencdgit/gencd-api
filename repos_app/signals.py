from django.db import connection, transaction
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from . import models
from django.contrib.auth import get_user_model
     

@receiver(post_save, sender=models.Invitation)
def send_invitation_email(sender, instance, created, **kwargs):
    """
    Sends an invitation email to the recipient when an invitation is created.
    """
    if created:
        instance.send_invitation_email()
      
@receiver(pre_delete, sender=get_user_model())
def delete_related_foreign_keys(sender, instance, **kwargs):
    user_id = str(instance.id)

    # Define known FK chains that need cascading cleanup manually
    # (parent_table, child_table, parent_fk_col_on_child_table)
    continued_fks = [
        ("gpt_suite_app_conversation", "gpt_suite_app_message", "conversation_id"),
    ]

    with transaction.atomic(), connection.cursor() as cursor:
        # Step 1: Handle known FK chains
        for parent_table, child_table, child_fk_column in continued_fks:
            # Fetch conversations for user
            cursor.execute(f'SELECT id FROM "{parent_table}" WHERE user_id = %s', [user_id])
            parent_ids = [row[0] for row in cursor.fetchall()]
            if not parent_ids:
                continue

            # Delete related child rows
            sql_in = ",".join(["%s"] * len(parent_ids))
            cursor.execute(
                f'DELETE FROM "{child_table}" WHERE "{child_fk_column}" IN ({sql_in})',
                parent_ids
            )

            # Then delete parent rows
            cursor.execute(
                f'DELETE FROM "{parent_table}" WHERE user_id = %s',
                [user_id]
            )

        # Step 2: Handle remaining direct FKs to user (if any)
        cursor.execute("""
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name
            FROM
                information_schema.table_constraints AS tc
            JOIN
                information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.constraint_schema = kcu.constraint_schema
            JOIN
                information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                 AND ccu.constraint_schema = tc.constraint_schema
            WHERE
                tc.constraint_type = 'FOREIGN KEY'
                AND ccu.table_name = %s
                AND ccu.column_name = %s;
        """, [get_user_model()._meta.db_table, get_user_model()._meta.pk.column])

        fk_references = cursor.fetchall()

        for schema, table, column in fk_references:
            if any(table == parent for parent, _, _ in continued_fks):
                # Already handled above
                continue

            full_table = f'"{schema}"."{table}"' if schema != 'public' else f'"{table}"'
            delete_sql = f'DELETE FROM {full_table} WHERE "{column}" = %s'
            cursor.execute(delete_sql, [user_id])
        
        
@receiver([post_save, post_delete], sender=models.Repository)
def update_repository_count(sender, instance, **kwargs):
    project = instance.project
    project.repository_count = project.repositories.count()
    project.save(update_fields=['repository_count'])
