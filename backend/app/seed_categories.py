import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models.category import Category


DEFAULT_CATEGORIES = [
    {"name": "BridgeDomain", "description": "L3 domain objects."},
    {"name": "Connectivity-P2P", "description": "point to point links connectivity"},
    {"name": "Controllers", "description": "The details are regarding controllers in the datacenter"},
    {"name": "Data Networks", "description": "For data network purposes"},
    {"name": "Firewall-Core", "description": "Main firewall clusters (like Checkpoint Maestro, inter-DC firewalls)"},
    {"name": "Firewall-HA", "description": "Sync / failover links and clusters."},
    {"name": "Firewall-InternalSeg", "description": "East-West segmentation firewalls."},
    {"name": "Firewall-Perimeter", "description": "Internet edge / site perimeter firewalls."},
    {"name": "L3Out", "description": "Purpose of L3out configuration"},
    {"name": "LB-GTM", "description": "Global DNS / site redirection."},
    {"name": "LB-HA", "description": "Sync / failover links and clusters."},
    {"name": "LB-InB", "description": "Mgmt interfaces Inband."},
    {"name": "LB-LTM", "description": "Local traffic load balancing (VIPs, pools)."},
    {"name": "LB-OOB", "description": "Mgmt interfaces, OOB"},
    {"name": "LB-WAF", "description": "Application firewall module (ASM)."},
    {"name": "Management-InBand", "description": "InBand Management purposes"},
    {"name": "Management-OOB", "description": "OOB Management purposes"},
    {"name": "Overlay", "description": "For overlay purposes"},
    {"name": "Security-Management", "description": "OOB mgmt, policy servers, logging nodes."},
    {"name": "ServiceGraph", "description": "Chained service insertion (Firewall + LB)."},
    {"name": "Underlay", "description": "For underlay purposes"},
    {"name": "VPN-Gateway", "description": "Site-to-Site VPNs, remote access VPN endpoints."}
]


async def ensure_categories() -> None:
    """Ensure default categories exist in the database"""
    async with AsyncSessionLocal() as session:
        categories_added = 0
        for category_data in DEFAULT_CATEGORIES:
            q = select(Category).where(Category.name == category_data["name"])
            res = await session.execute(q)
            existing_category = res.scalar_one_or_none()
            
            if existing_category is None:
                category = Category(
                    name=category_data["name"],
                    description=category_data["description"]
                )
                session.add(category)
                categories_added += 1
        
        await session.commit()
        print(f"Default categories seeded successfully ({categories_added} new categories added)")


async def main() -> None:
    await ensure_categories()


if __name__ == "__main__":
    asyncio.run(main())
