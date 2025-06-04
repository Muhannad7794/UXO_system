# danger_score/models.py

# This file is for defining Django models specific to the 'danger_score' application.
# If this app primarily provides calculation logic, utility functions, or management commands
# and does not have its own database tables, this file can remain empty or
# only contain imports if other parts of this app need them (though that's less common for models.py).

# from django.db import models # Uncomment if you decide to add models to this app later

# The signal handler that was previously in this file for calculating UXORecord.danger_score
# has been consolidated into 'uxo_records/signals.py'. This is to ensure that
# signals related to a specific model (UXORecord) are managed within that model's app
# and to avoid duplicate signal registrations.

# If the 'danger_score' app needs to define its own database models in the future,
# they would be defined here. For now, based on its role as a logic provider,
# it may not need any.
