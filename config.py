import os

# Secret Key
SECRET_KEY = 'team7'

# Database Configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Stripe Keys (Load from environment variables or use default for testing)
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'pk_test_51R1327JKMwWxJC9sqnVvScr2AtvKKIuOQWChTSiJNs5vagdfaRmwgbMkOqtUPXVrTS3ecIzILTe8tfsQd1uBczzI001dof0Kch')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_51R1327JKMwWxJC9sVfnEkayuhNi5oBfLWhrKtwDL0bogNn2SAIfcw0BLE2YMrpodi8cLxssPNe9gSdwjDeSb0xgH00b3S8JsMU')
