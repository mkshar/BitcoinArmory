################################################################################
#                                                                              #
# Copyright (C) 2011-2013, Armory Technologies, Inc.                           #
# Distributed under the GNU Affero General Public License (AGPL v3)            #
# See LICENSE or http://www.gnu.org/licenses/agpl.html                         #
#                                                                              #
################################################################################

from PyQt4.QtGui import *
from qtdefines import *
import signal
from PyQt4.Qt import *
from armoryengine.BDM import TheBDM
from armoryengine.ArmoryUtils import coin2str

################################################################################
class ArmoryFrame(QFrame):
   def __init__(self, parent=None, main=None):
      super(ArmoryFrame, self).__init__(parent)

      self.parent = parent
      self.main   = main

   def accept(self):
      self.parent.accpet()
      return


class SelectWalletFrame(ArmoryFrame):
   def __init__(self, parent=None, main=None, firstSelect=None, onlyMyWallets=False, \
                             wltIDList=None, atLeast=0, layoutDirection=HORIZONTAL, \
                             selectWltCallback=None):
      super(SelectWalletFrame, self).__init__(parent, main)

      self.walletComboBox = QComboBox()
      self.balAtLeast = atLeast
      self.selectWltCallback = selectWltCallback

      if self.main and len(self.main.walletMap) == 0:
         QMessageBox.critical(self, 'No Wallets!', \
            'There are no wallets to select from.  Please create or import '
            'a wallet first.', QMessageBox.Ok)
         self.accept()
         return
      
      self.wltIDList = wltIDList if not wltIDList == None else list(self.main.walletIDList)
      
      selectedWltIndex = 0
      self.selectedID = None
      wltItems = 0
      if len(self.wltIDList) > 0:
         self.selectedID = self.wltIDList[0]
         for wltID in self.wltIDList:
            wlt = self.main.walletMap[wltID]
            wlttype = determineWalletType(wlt, self.main)[0]
            if onlyMyWallets and wlttype == WLTTYPES.WatchOnly:
               continue
            self.walletComboBox.addItem(wlt.labelName)
         
            if wltID == firstSelect:
               selectedWltIndex = wltItems
               self.selectedID = wltID
            wltItems += 1
            
         self.walletComboBox.setCurrentIndex(selectedWltIndex)
      self.connect(self.walletComboBox, SIGNAL('currentIndexChanged(int)'), self.showWalletInfo)

      # Start the layout
      layout =  QVBoxLayout() 

      lbls = []
      lbls.append(QRichLabel("Wallet ID:", doWrap=False))
      lbls.append(QRichLabel("Name:", doWrap=False))
      lbls.append(QRichLabel("Description:", doWrap=False))
      lbls.append(QRichLabel("Spendable BTC:", doWrap=False))

      for i in range(len(lbls)):
         lbls[i].setAlignment(Qt.AlignLeft | Qt.AlignTop)
         lbls[i].setText('<b>' + str(lbls[i].text()) + '</b>')
         
      self.dispID = QRichLabel('')
      self.dispName = QRichLabel('')
      self.dispDescr = QRichLabel('')
      self.dispDescr.setWordWrap(True)
      self.dispBal = QMoneyLabel(0)

      self.dispBal.setTextFormat(Qt.RichText)
      
      wltInfoFrame = QFrame()
      wltInfoFrame.setFrameStyle(STYLE_SUNKEN)
      wltInfoFrame.setMaximumWidth(350)
      wltInfoFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
      frmLayout = QGridLayout()
      for i in range(len(lbls)):
         frmLayout.addWidget(lbls[i], i, 0, 1, 1)

      self.dispID.setAlignment(Qt.AlignLeft | Qt.AlignTop)
      self.dispName.setAlignment(Qt.AlignLeft | Qt.AlignTop)
      self.dispDescr.setAlignment(Qt.AlignLeft | Qt.AlignTop)
      self.dispBal.setAlignment(Qt.AlignLeft | Qt.AlignTop)
      self.dispDescr.setMinimumWidth(tightSizeNChar(self.dispDescr, 40)[0])
      frmLayout.addWidget(self.dispID, 0, 2, 1, 1)
      frmLayout.addWidget(self.dispName, 1, 2, 1, 1)
      frmLayout.addWidget(self.dispDescr, 2, 2, 1, 1)
      frmLayout.addWidget(self.dispBal, 3, 2, 1, 1)
      frmLayout.addItem(QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Expanding), 0, 1, 3, 1)
      wltInfoFrame.setLayout(frmLayout)
      layout.addWidget(makeLayoutFrame(layoutDirection, [self.walletComboBox, wltInfoFrame]) )
      self.setLayout(layout)

   def showWalletInfo(self, i=0):
      currentWltIndex = self.walletComboBox.currentIndex()
      wltID = self.wltIDList[currentWltIndex]
      wlt = self.main.walletMap[wltID]
      self.dispID.setText(wltID)
      self.dispName.setText(wlt.labelName)
      self.dispDescr.setText(wlt.labelDescr)
      self.selectedID = wltID
      
      if not TheBDM.getBDMState() == 'BlockchainReady':
         self.dispBal.setText('-' * 12)
      else:
         bal = wlt.getBalance('Spendable')
         balStr = coin2str(wlt.getBalance('Spendable'), maxZeros=1)
         if bal <= self.balAtLeast:
            self.dispBal.setText('<font color="red"><b>%s</b></font>' % balStr)
         else:
            self.dispBal.setText('<b>' + balStr + '</b>')     
      if self.selectWltCallback:
         self.selectWltCallback(wlt)


   #############################################################################
   def setWalletSummary(self):
      useAllAddr = (self.altBalance == None)
      fullBal = self.wlt.getBalance('Spendable')
      if useAllAddr:
         self.lblSummaryID.setText(self.wlt.uniqueIDB58)
         self.lblSummaryName.setText(self.wlt.labelName)
         self.lblSummaryDescr.setText(self.wlt.labelDescr)
         if fullBal == 0:
            self.lblSummaryBal.setText('0.0', color='TextRed', bold=True)
         else:
            self.lblSummaryBal.setValueText(fullBal, wBold=True)
      else:
         self.lblSummaryID.setText(self.wlt.uniqueIDB58 + '*')
         self.lblSummaryName.setText(self.wlt.labelName + '*')
         self.lblSummaryDescr.setText('*Coin Control Subset*', color='TextBlue', bold=True)
         self.lblSummaryBal.setText(coin2str(self.altBalance, maxZeros=0), color='TextBlue')
         rawValTxt = str(self.lblSummaryBal.text())
         self.lblSummaryBal.setText(rawValTxt + ' <font color="%s">(of %s)</font>' % \
                                    (htmlColor('DisableFG'), coin2str(fullBal, maxZeros=0)))

      if not TheBDM.getBDMState() == 'BlockchainReady':
         self.lblSummaryBal.setText('(available when online)', color='DisableFG')