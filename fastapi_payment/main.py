import os
from pathlib import Path
from dotenv import load_dotenv
import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, Transaction
from .schemas import PaymentRequest, PaymentResponse, TransactionStatusResponse
from .payment_service import PaymentService

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('FASTAPI_SECRET_KEY', os.getenv('DJANGO_SECRET_KEY', 'django-insecure-payment-system-super-secret-key-change-in-prod'))
ALGORITHM = 'HS256'

app = FastAPI(
    title="Payment Processing Engine (FastAPI)",
    description="High-performance asynchronous payment microservice with JWT authentication and payment simulation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials: user_id missing in token"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    return user


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Payment Processing Engine",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.post("/api/payments/pay", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED, tags=["Payments"])
def make_payment(
    payment_data: PaymentRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Make a Payment (MODULE 3)
    - Validates saved card belonging to authenticated user
    - Creates initial transaction with status: PENDING
    - Simulates gateway response -> Final Status: SUCCESS or FAILED
    - Records audit log
    - Does NOT store CVV
    """
    client_ip = request.client.host if request.client else "127.0.0.1"

    try:
        transaction = PaymentService.process_payment(
            db=db,
            payment_data=payment_data,
            user_id=current_user.id,
            client_ip=client_ip
        )
        return transaction
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Payment processing error: {str(exc)}")


@app.get("/api/payments/status/{transaction_id}", response_model=TransactionStatusResponse, tags=["Payments"])
def check_transaction_status(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check payment transaction status by transaction_id."""
    txn = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")

    return txn
