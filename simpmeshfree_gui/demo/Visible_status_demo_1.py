from simpmeshfree_gui.samples import gen_GeomUtils
from simpmeshfree_gui.jvm_utils import start_jvm
from simpmeshfree_gui.plot2d import GeomUtilsPainter, SupportDomainPainter
import matplotlib.pyplot as plt
from jpype import JClass

if __name__ == '__main__':
    start_jvm(debug_port=8998)
    geomUtils = gen_GeomUtils(size=3, quality_area=10)
    
    plt.ioff()
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    fig.show()

    geomUtils_painter = GeomUtilsPainter(ax, geomUtils)
    geomUtils_painter.plot()
    geomUtils_painter.draw()
    
    fig.show()
    
    spd_painter = SupportDomainPainter(ax, geomUtils)

    Coordinate = JClass('net.epsilony.utils.geom.Coordinate')
    center = Coordinate()
    
    center.x = 60.0
    center.y = 30.0
    radius = 20.0
    
    bndList = geomUtils.searchBoundary(center, radius, None)
    spaceNodes = geomUtils.searchSpaceNodes(center, radius, None)
    bndNodes = geomUtils.getBndsNodes(bndList, None)
    
    spd_painter.plot(centerCoord=center, radius=radius)
    spd_painter.draw()
