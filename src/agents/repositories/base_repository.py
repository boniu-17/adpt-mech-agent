"""
基础Repository - 提供通用CRUD操作
"""

from typing import Type, TypeVar, Optional, List, Dict, Any, Generic, cast

from sqlalchemy import select, func, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """基础Repository - 减少重复代码"""

    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    @staticmethod
    def scalars_to_list(scalar_result: ScalarResult) -> List[T]:
        """安全地将ScalarResult转换为List[T]"""
        # 这里使用cast，因为scalars()返回的是ScalarResult[Unknown]
        # 但我们在使用scalars()时知道它返回的是T类型
        typed_scalar_result = cast(ScalarResult[T], scalar_result)
        # all()返回Sequence[T]，我们需要转换为List[T]
        return list(typed_scalar_result.all())

    async def get(self, id: int) -> Optional[T]:
        """根据ID获取"""
        return await self.session.get(self.model_class, id)

    async def get_by(self, **filters) -> Optional[T]:
        """根据条件获取单个"""
        stmt = select(self.model_class).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, **filters) -> List[T]:
        """根据条件列表"""
        stmt = select(self.model_class).filter_by(**filters)
        result = await self.session.execute(stmt)
        return self.scalars_to_list(result.scalars())

    async def create(self, **data) -> T:
        """创建记录"""
        instance = self.model_class(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, id: int, **data) -> Optional[T]:
        """更新记录"""
        instance = await self.get(id)
        if instance:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await self.session.flush()
        return instance

    async def delete(self, id: int) -> bool:
        """删除记录"""
        instance = await self.get(id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
            return True
        return False

    async def exists(self, **filters) -> bool:
        """检查记录是否存在"""
        stmt = select(func.count()).select_from(self.model_class).filter_by(**filters)
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def count(self, **filters) -> int:
        """统计记录数量"""
        stmt = select(func.count()).select_from(self.model_class).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def paginate(self, page: int = 1, page_size: int = 20, **filters) -> Dict[str, Any]:
        """分页查询"""
        offset = (page - 1) * page_size

        # 查询数据
        stmt = select(self.model_class).filter_by(**filters).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        # 查询总数
        total = await self.count(**filters)

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    async def create_or_update(self, filters: Dict, defaults: Dict) -> T:
        """创建或更新记录"""
        existing = await self.get_by(**filters)
        if existing:
            return await self.update(existing.id, **defaults)
        else:
            data = {**filters, **defaults}
            return await self.create(**data)

    async def bulk_create(self, items: List[Dict[str, Any]]) -> List[T]:
        """批量创建记录"""
        instances = []
        for item in items:
            instance = self.model_class(**item)
            instances.append(instance)

        self.session.add_all(instances)
        await self.session.flush()
        return instances
