from sqlalchemy.orm import Session
from repositories.customer_repository import CustomerRepository
from schemas.customer import CustomerCreate
from models.customer import Customer

class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)

    def get_customer_list(self, search: str = None):
        customers = self.repo.get_customers(search)
        
        # 为了兼容前端 CustomerList 页面，我们附带上从属于它的联系人列表
        for customer in customers:
            # SQLAlchemy 的关系可能会延迟加载或者没设置 back_populates 到 contact
            # 因为 models/customer.py 里 Contact 表没有声明关联。我们手动查询一下
            from models.customer import Contact
            contacts = self.repo.db.query(Contact).filter(Contact.customer_id == customer.id).all()
            customer.contacts = contacts
            
        return customers

    def get_customer_detail(self, customer_id: int):
        customer = self.repo.get_customer_by_id(customer_id)
        if customer:
            from models.customer import Contact
            from models.equipment import Equipment
            contacts = self.repo.db.query(Contact).filter(Contact.customer_id == customer.id).all()
            equipments = self.repo.db.query(Equipment).filter(Equipment.customer_id == customer.id).all()
            customer.contacts = contacts
            customer.equipments = equipments
        return customer

    def create_customer(self, data: CustomerCreate, user_id: int) -> Customer:
        """新建客户，同时写入操作审计日志"""
        return self.repo.create_customer(data, user_id)
