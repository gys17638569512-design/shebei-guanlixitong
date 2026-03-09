from sqlalchemy.orm import Session
from models.customer import Customer, Contact
from schemas.customer import CustomerCreate
from core.audit import write_audit_log

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_customers(self, search: str = None):
        query = self.db.query(Customer)
        if search:
            query = query.filter(
                (Customer.company_name.contains(search)) |
                (Customer.contact_name.contains(search))
            )
        return query.all()

    def get_customer_by_id(self, customer_id: int):
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def create_customer(self, customer_data: CustomerCreate, user_id: int) -> Customer:
        # 创建主客户记录
        db_customer = Customer(
            company_name=customer_data.company_name,
            contact_name=customer_data.contact_name,
            contact_phone=customer_data.contact_phone,
            address=customer_data.address
        )
        self.db.add(db_customer)
        self.db.flush()  # 获取插入后的 ID

        # 关联附带的其它联系人
        if customer_data.contacts:
            for contact in customer_data.contacts:
                db_contact = Contact(
                    customer_id=db_customer.id,
                    name=contact.name,
                    phone=contact.phone,
                    position=contact.position
                )
                self.db.add(db_contact)

        # 写入操作审计日志 - PRD 铁律：所有写操作必须记录
        write_audit_log(
            db=self.db,
            user_id=user_id,
            action="CREATE",
            table_name="customers",
            record_id=db_customer.id,
            new_value={"company_name": db_customer.company_name, "contact_name": db_customer.contact_name}
        )

        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer
