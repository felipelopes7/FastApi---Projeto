from fastapi import APIRouter, HTTPException, Depends
from dependencies import pegar_sessao, verificar_token
from sqlalchemy.orm import Session
from schemas import PedidoSchema, ItemPedidoSchema,ResponsePedidoSchema
from database.models import Pedido, Usuario, ItemPedido
from typing import List

order_router = APIRouter(prefix='/order', tags=['orders'], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():



    return {"Mensagem": "Você acessou a tela de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session = Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {'Mensagem': f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    #
    #
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="PEDIDO NÃO ENCONTRADO")
    
    if not usuario.admin and usuario.id != pedido.usuario:
        raise  HTTPException(status_code=401, detail="AÇÃO NÃO AUTORIZADA")


    pedido.status = "CANCELADO"
    session.commit()
    return{
        "mensagem": f"Pedido número: {pedido.id} cancelado com sucesso",
        "pedido": pedido
    }

@order_router.get("/listar")
async def listar_pedidos(usuario: Usuario = Depends(verificar_token), session:Session = Depends(pegar_sessao)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="AÇÃO NÃO PERMITIDA")
    else:
        pedidos = session.query(Pedido).all()
        return{"pedidos": pedidos}
    
@order_router.post("/pedido/adicionar-item-item/{id_pedido}")
async def adc_item(id_pedido, 
                   item_pedido_schema: ItemPedidoSchema, 
                   session: Session = Depends(pegar_sessao), 
                   usuario: Usuario= Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="AÇÃO NÃO PERMITIDA")
    item_pedido = ItemPedido(item_pedido_schema.quantidade,
                             item_pedido_schema.sabor,
                             item_pedido_schema.tamanho,
                             item_pedido_schema.preco_unitario,
                             id_pedido)
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return{
        "mensagem": "Item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }

@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int,
                            session: Session = Depends(pegar_sessao),
                            usuario: Usuario = Depends(verificar_token)):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id==item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item no pedido não existente")
    if not usuario.admin and usuario.id != item_pedido.pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
    session.delete(item_pedido)
    item_pedido.pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item removido com sucesso",
        "preco_pedido": pedido.preco,
        "pedido": item_pedido.pedido
    }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    pedido.status = "FINALIZADO"
    session.commit()
    return {
        "mensagem": f"Pedido número: {pedido.id} finalizado com sucesso",
        "pedido": pedido
    }

@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    return {
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

# visualizar todos os pedidos de 1 usuário
@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema])
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    return pedidos
