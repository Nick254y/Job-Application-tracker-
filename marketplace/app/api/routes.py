from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Payment as PaymentModel
from app.services.receipt import send_payment_receipt
from app.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])


class PaymentCreate(BaseModel):
    client_name: str
    property_name: str
    amount: float
    payment_method: str = "cash"
    notes: str = ""


class PaymentResponse(BaseModel):
    id: int
    client_name: str
    property_name: str
    amount: float
    payment_method: str
    status: str
    notes: str
    created_at: datetime
    paid_at: datetime | None

    class Config:
        from_attributes = True
        # Serialize datetime to string for JSON responses
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def get_db():
    from app.models import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    """Create a new payment record and send receipt."""
    db_payment = PaymentModel(
        client_name=payment.client_name,
        property_name=payment.property_name,
        amount=payment.amount,
        payment_method=payment.payment_method,
        notes=payment.notes,
        status="paid",
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Send receipt to client
    send_payment_receipt(
        client_email=f"{payment.client_name.lower().replace(' ', '.')}@example.com",
        client_name=payment.client_name,
        property_name=payment.property_name,
        amount=payment.amount,
        payment_id=db_payment.id,
        status="paid",
    )

    return db_payment


@router.get("/", response_model=List[PaymentResponse])
def list_payments(
    status: Optional[str] = None,
    client_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all payments with optional filters."""
    query = db.query(PaymentModel)
    if status:
        query = query.filter(PaymentModel.status == status)
    if client_name:
        query = query.filter(PaymentModel.client_name.contains(client_name))
    return query.all()


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """Get a specific payment by ID."""
    payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.put("/{payment_id}/mark-paid", response_model=PaymentResponse)
def mark_payment_paid(payment_id: int, db: Session = Depends(get_db)):
    """Mark a payment as paid (for manual confirmation)."""
    payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = "paid"
    payment.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(payment)
    return payment


@router.put("/{payment_id}/mark-overdue", response_model=PaymentResponse)
def mark_payment_overdue(payment_id: int, db: Session = Depends(get_db)):
    """Mark a payment as overdue."""
    payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = "overdue"
    db.commit()
    db.refresh(payment)
    return payment
