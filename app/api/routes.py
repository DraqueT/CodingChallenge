from fastapi import APIRouter, Depends

from app.models.api import OrderRouteRequest, OrderRouteResponse
from app.repositories.fixtures import FixtureRepository, get_repository
from app.services.routing import RoutingService

router = APIRouter()


def get_routing_service(
    repository: FixtureRepository = Depends(get_repository),
) -> RoutingService:
    return RoutingService(repository)


@router.post("/orders/route", response_model=OrderRouteResponse)
def route_order(
    order: OrderRouteRequest,
    routing_service: RoutingService = Depends(get_routing_service),
) -> OrderRouteResponse:
    return routing_service.route_order(order)
