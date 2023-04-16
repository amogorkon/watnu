from PyQt6.QtCore import QRectF, QSizeF, Qt
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView


class Node(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.edges = []
        self.color = QColor(Qt.GlobalColor.white)
        self.pen = QPen(Qt.PenStyle.NoPen)

    def boundingRect(self):
        return QRectF(-10, -10, 20, 20)

    def paint(self, painter, option, widget):
        painter.setBrush(self.color)
        painter.setPen(self.pen)
        painter.drawEllipse(-10, -10, 20, 20)


class Edge(QGraphicsItem):
    def __init__(self, sourceNode, destNode):
        super().__init__()
        self.sourcePoint = sourceNode
        self.destPoint = destNode
        self.color = QColor(Qt.GlobalColor.black)
        self.pen = QPen(Qt.PenStyle.SolidLine)

    def boundingRect(self):
        extra = (self.pen.width() + 20) / 2.0
        return (
            QRectF(
                self.sourcePoint.pos(),
                QSizeF(
                    self.destPoint.pos().x() - self.sourcePoint.pos().x(),
                    self.destPoint.pos().y() - self.sourcePoint.pos().y(),
                ),
            )
            .normalized()
            .adjusted(-extra, -extra, extra, extra)
        )

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawLine(self.sourcePoint.pos(), self.destPoint.pos())


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    scene = QGraphicsScene()
    view = QGraphicsView(scene)

    node1 = Node()
    node2 = Node()
    node3 = Node()

    edge1 = Edge(node1, node2)
    edge2 = Edge(node2, node3)

    scene.addItem(node1)
    scene.addItem(node2)
    scene.addItem(node3)

    scene.addItem(edge1)
    scene.addItem(edge2)

    view.show()

    sys.exit(app.exec())
