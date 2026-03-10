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

    def update_customer(self, customer_id: int, data, user_id: int) -> Customer:
        """ 更新客户基本信息及联系人列表 """
        customer = self.repo.get_customer_by_id(customer_id)
        if not customer:
            from core.exceptions import NotFoundError
            raise NotFoundError("客户未找到")
        
        update_data = data.model_dump(exclude_unset=True)
        # 提取 contacts 数组进行特殊处理
        contacts_data = update_data.pop("contacts", None)
        
        # 更新基本字段
        for key, value in update_data.items():
            setattr(customer, key, value)
            
        # 如果携带了 contacts，覆盖原有联系人
        if contacts_data is not None:
            from models.customer import Contact
            # 删除旧有联系人
            self.repo.db.query(Contact).filter(Contact.customer_id == customer_id).delete()
            # 插入新联系人
            for c_data in contacts_data:
                new_contact = Contact(
                    customer_id=customer.id,
                    name=c_data["name"],
                    phone=c_data["phone"],
                    position=c_data.get("position", "其它联系人")
                )
                self.repo.db.add(new_contact)
                
        self.repo.db.flush()
        self.repo.db.commit()
        return customer

    def delete_customer(self, customer_id: int, user_id: int) -> bool:
        """删除客户（确保没有依赖工单）"""
        customer = self.repo.get_customer_by_id(customer_id)
        if not customer:
            from core.exceptions import NotFoundError
            raise NotFoundError("客户未找到")
        from models.work_order import WorkOrder
        existing_orders = self.repo.db.query(WorkOrder).filter(WorkOrder.customer_id == customer_id).count()
        if existing_orders > 0:
            from core.exceptions import BusinessError
            raise BusinessError("该客户名下还有进行中的工单记录，无法删除")
        self.repo.db.delete(customer)
        self.repo.db.commit()
        return True
