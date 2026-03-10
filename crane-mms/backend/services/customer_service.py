from sqlalchemy.orm import Session
from repositories.customer_repository import CustomerRepository
from schemas.customer import CustomerCreate
from models.customer import Customer

class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)

    def get_customer_list(self, search: str = None, current_user=None):
        query = self.repo.db.query(Customer)
        
        # MANAGER 只能看自己负责的客户（通过工单关联判断）
        if current_user and current_user.role == "MANAGER":
            # 通过已有工单关联找到该经理相关的客户ID
            from models.work_order import WorkOrder
            from models.user import User
            managed_customer_ids = self.repo.db.query(WorkOrder.customer_id).filter(
                WorkOrder.technician_id.in_(
                    self.repo.db.query(User.id).filter(User.manager_id == current_user.id)
                )
            ).distinct().all()
            customer_ids = [cid for (cid,) in managed_customer_ids]
            if customer_ids:
                query = query.filter(Customer.id.in_(customer_ids))
            else:
                # 如果该经理名下暂时没有关联的工单/客户，返回空列表
                return []
        
        if search:
            query = query.filter(
                (Customer.company_name.contains(search)) |
                (Customer.contact_name.contains(search))
            )
        
        customers = query.all()
        
        # 为了兼容前端 CustomerList 页面，我们附带上从属于它的联系人列表
        for customer in customers:
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
