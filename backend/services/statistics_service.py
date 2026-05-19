from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.expense import Expense
from models.expense_category import ExpenseCategory
from models.expense_tag import ExpenseTag
from models.expense_tag_index import ExpenseTagIndex
from schemas.statistics import (
    OverviewResponse, CategoryStatItem, TagStatItem, MonthlyStatItem,
    MonthlyCategoryDetail, MonthlyTagDetail,
)


async def overview(db: AsyncSession, uid: int) -> OverviewResponse:
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz)

    today_start = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    today_end = int((now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

    weekday = now.weekday()
    week_start_dt = (now - timedelta(days=weekday)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = int(week_start_dt.timestamp())

    month_start = int(now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())

    year_start = int(now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())

    today_total = await _sum_amount(db, uid, today_start, today_end)
    week_total = await _sum_amount(db, uid, week_start, today_end)
    month_total = await _sum_amount(db, uid, month_start, today_end)
    year_total = await _sum_amount(db, uid, year_start, today_end)

    return OverviewResponse(
        today=today_total,
        this_week=week_total,
        this_month=month_total,
        this_year=year_total,
    )


async def by_category(
    db: AsyncSession,
    uid: int,
    start_time: int | None = None,
    end_time: int | None = None,
    tag_ids: str | None = None,
) -> list[CategoryStatItem]:
    base_query = select(
        Expense.category_id,
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("cnt"),
    ).where(Expense.uid == uid, Expense.deleted == 0)

    base_query = _apply_filters(base_query, start_time, end_time, tag_ids)
    base_query = base_query.group_by(Expense.category_id)

    result = await db.execute(base_query)
    rows = result.all()

    if not rows:
        return []

    grand_total = sum(row.total for row in rows)

    cat_ids = [row.category_id for row in rows]
    cat_result = await db.execute(
        select(ExpenseCategory).where(ExpenseCategory.id.in_(cat_ids))
    )
    cat_map = {c.id: c for c in cat_result.scalars().all()}

    items = []
    for row in rows:
        cat = cat_map.get(row.category_id)
        items.append(CategoryStatItem(
            category_id=row.category_id,
            category_name=cat.name if cat else "未知",
            category_icon=cat.icon if cat else "📦",
            category_color=cat.color if cat else "#607D8B",
            total_amount=row.total,
            percentage=round(row.total / grand_total * 100, 1) if grand_total > 0 else 0,
            transaction_count=row.cnt,
        ))

    items.sort(key=lambda x: x.total_amount, reverse=True)
    return items


async def by_tag(
    db: AsyncSession,
    uid: int,
    start_time: int | None = None,
    end_time: int | None = None,
    category_ids: str | None = None,
) -> list[TagStatItem]:
    base_query = select(
        ExpenseTagIndex.tag_id,
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("cnt"),
    ).join(Expense, Expense.id == ExpenseTagIndex.expense_id).where(
        ExpenseTagIndex.uid == uid,
        Expense.deleted == 0,
    )

    base_query = _apply_filters(base_query, start_time, end_time, category_ids=category_ids)
    base_query = base_query.group_by(ExpenseTagIndex.tag_id)

    result = await db.execute(base_query)
    rows = result.all()

    if not rows:
        return []

    grand_total = sum(row.total for row in rows)

    tag_ids_list = [row.tag_id for row in rows]
    tag_result = await db.execute(
        select(ExpenseTag).where(ExpenseTag.id.in_(tag_ids_list), ExpenseTag.deleted == 0)
    )
    tag_map = {t.id: t for t in tag_result.scalars().all()}

    items = []
    for row in rows:
        tag = tag_map.get(row.tag_id)
        if not tag:
            continue
        items.append(TagStatItem(
            tag_id=row.tag_id,
            tag_name=tag.name,
            total_amount=row.total,
            percentage=round(row.total / grand_total * 100, 1) if grand_total > 0 else 0,
            transaction_count=row.cnt,
        ))

    items.sort(key=lambda x: x.total_amount, reverse=True)
    return items


async def monthly(
    db: AsyncSession,
    uid: int,
    start_year: int | None = None,
    start_month: int | None = None,
    end_year: int | None = None,
    end_month: int | None = None,
    category_ids: str | None = None,
    tag_ids: str | None = None,
) -> list[MonthlyStatItem]:
    now = datetime.now(timezone.utc)
    sy = start_year or now.year
    sm = start_month or 1
    ey = end_year or now.year
    em = end_month or now.month

    start_ts = int(datetime(sy, sm, 1, tzinfo=timezone.utc).timestamp())
    if em == 12:
        end_ts = int(datetime(ey + 1, 1, 1, tzinfo=timezone.utc).timestamp())
    else:
        end_ts = int(datetime(ey, em + 1, 1, tzinfo=timezone.utc).timestamp())

    base_query = select(
        Expense.id,
        Expense.amount,
        Expense.category_id,
        Expense.transaction_time,
    ).where(
        Expense.uid == uid,
        Expense.deleted == 0,
        Expense.transaction_time >= start_ts,
        Expense.transaction_time < end_ts,
    )

    base_query = _apply_filters(base_query, tag_ids=tag_ids, category_ids=category_ids)

    result = await db.execute(base_query)
    rows = result.all()

    if not rows:
        return []

    cat_ids_all = list(set(r.category_id for r in rows))
    cat_result = await db.execute(
        select(ExpenseCategory).where(ExpenseCategory.id.in_(cat_ids_all))
    )
    cat_map = {c.id: c for c in cat_result.scalars().all()}

    tz = timezone(timedelta(hours=8))
    monthly_data: dict[tuple[int, int], dict] = {}

    for row in rows:
        dt = datetime.fromtimestamp(row.transaction_time, tz=tz)
        key = (dt.year, dt.month)

        if key not in monthly_data:
            monthly_data[key] = {"total": 0, "count": 0, "by_cat": {}}
        monthly_data[key]["total"] += row.amount
        monthly_data[key]["count"] += 1
        monthly_data[key]["by_cat"][row.category_id] = \
            monthly_data[key]["by_cat"].get(row.category_id, 0) + row.amount

    # 按标签聚合
    expense_ids = [r.id for r in rows]
    expense_amount_map = {r.id: r.amount for r in rows}
    expense_month_map: dict[int, tuple[int, int]] = {}
    for row in rows:
        dt = datetime.fromtimestamp(row.transaction_time, tz=tz)
        expense_month_map[row.id] = (dt.year, dt.month)

    tag_result = await db.execute(
        select(ExpenseTagIndex.expense_id, ExpenseTagIndex.tag_id).where(
            ExpenseTagIndex.expense_id.in_(expense_ids),
            ExpenseTagIndex.uid == uid,
        )
    )
    tag_rows = tag_result.all()

    tag_map: dict[int, str] = {}
    monthly_tag_data: dict[tuple[int, int], dict[int, int]] = {}
    if tag_rows:
        tag_ids_all = list(set(tr.tag_id for tr in tag_rows))
        tag_result2 = await db.execute(
            select(ExpenseTag).where(ExpenseTag.id.in_(tag_ids_all))
        )
        tag_map = {t.id: t.name for t in tag_result2.scalars().all()}

        for tr in tag_rows:
            key = expense_month_map.get(tr.expense_id)
            if key:
                if key not in monthly_tag_data:
                    monthly_tag_data[key] = {}
                monthly_tag_data[key][tr.tag_id] = \
                    monthly_tag_data[key].get(tr.tag_id, 0) + expense_amount_map[tr.expense_id]

    items = []
    for key in sorted(monthly_data.keys()):
        data = monthly_data[key]
        by_cat = []
        for cid, amt in data["by_cat"].items():
            cat = cat_map.get(cid)
            by_cat.append(MonthlyCategoryDetail(
                category_id=cid,
                category_name=cat.name if cat else "未知",
                category_icon=cat.icon if cat else "📦",
                category_color=cat.color if cat else "#607D8B",
                amount=amt,
            ))
        by_cat.sort(key=lambda x: x.amount, reverse=True)

        by_tag = []
        tag_data = monthly_tag_data.get(key, {})
        for tid, amt in tag_data.items():
            tname = tag_map.get(tid, "未知")
            by_tag.append(MonthlyTagDetail(tag_id=tid, tag_name=tname, amount=amt))
        by_tag.sort(key=lambda x: x.amount, reverse=True)

        items.append(MonthlyStatItem(
            year=key[0],
            month=key[1],
            total_amount=data["total"],
            transaction_count=data["count"],
            by_category=by_cat,
            by_tag=by_tag,
        ))

    return items


async def _sum_amount(db: AsyncSession, uid: int, start: int, end: int) -> int:
    result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.uid == uid,
            Expense.deleted == 0,
            Expense.transaction_time >= start,
            Expense.transaction_time < end,
        )
    )
    return result.scalar()


def _apply_filters(query, start_time=None, end_time=None, tag_ids=None, category_ids=None):
    if start_time is not None:
        query = query.where(Expense.transaction_time >= int(start_time))
    if end_time is not None:
        query = query.where(Expense.transaction_time <= int(end_time))
    if tag_ids:
        ids = [int(t) for t in tag_ids.split(",") if t.strip()]
        if ids:
            tag_subquery = select(ExpenseTagIndex.expense_id).where(
                ExpenseTagIndex.tag_id.in_(ids),
                ExpenseTagIndex.uid == Expense.uid,
            ).subquery()
            query = query.where(Expense.id.in_(tag_subquery))
    if category_ids:
        ids = [int(c) for c in category_ids.split(",") if c.strip()]
        if ids:
            query = query.where(Expense.category_id.in_(ids))
    return query
