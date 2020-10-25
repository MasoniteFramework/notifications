from orator.migrations import Migration


class CreateNotificationsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("notifications") as table:
            table.increments("id")
            table.string("type")
            table.text("data")
            table.morphs("notifiable")
            table.datetime("read_at").nullable()
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("notifications")
