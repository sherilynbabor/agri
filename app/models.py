from app import db
from datetime import datetime, timedelta


# 🌱 USER MODEL
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    crops = db.relationship(
        "Crop",
        backref="owner",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.username}>"


# 🌾 CROP MODEL
class Crop(db.Model):
    __tablename__ = "crop"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    growth_stage = db.Column(db.String(50), default="Seed 🌱")
    image = db.Column(db.String(200), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # ✅ FIX: safer default datetime (important for production)
    date_planted = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow()
    )

    days_to_harvest = db.Column(db.Integer, default=60)

    # 🤖 AI DETECTION FIELDS
    disease = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    last_scanned = db.Column(db.DateTime, nullable=True)

    # -------------------------
    # SAFE PROPERTIES
    # -------------------------
    @property
    def harvest_date(self):
        if not self.date_planted:
            return None
        return self.date_planted + timedelta(days=self.days_to_harvest)

    @property
    def remaining_days(self):
        if not self.harvest_date:
            return 0

        # ⚠️ FIX: safer comparison logic (prevents negative weird values)
        delta = self.harvest_date - datetime.utcnow()
        return max(delta.days, 0)

    @property
    def progress(self):
        if self.days_to_harvest <= 0:
            return 100

        grown = self.days_to_harvest - self.remaining_days
        progress = int((grown / self.days_to_harvest) * 100)

        return max(0, min(100, progress))

    # -------------------------
    # 🤖 HELPER METHOD
    # -------------------------
    def update_scan(self, disease, confidence):
        """
        Update crop with AI scan result
        """
        self.disease = disease
        self.confidence = confidence
        self.last_scanned = datetime.utcnow()

    def __repr__(self):
        return f"<Crop {self.name} - {self.growth_stage}>"