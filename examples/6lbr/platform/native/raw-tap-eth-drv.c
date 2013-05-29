#include "contiki.h"
#include "contiki-lib.h"
#include "contiki-net.h"
#include "net/uip.h"
#include "string.h"

#include "cetic-6lbr.h"
#include "eth-drv.h"
#include "raw-tap-dev.h"
#include "nvm-config.h"
#include "slip-config.h"
#include "sicslow-ethernet.h"
//Temporary, should be removed
#include "native-rdc.h"

#define DEBUG 1
#include "net/uip-debug.h"

#if DEBUG
#define PRINTETHADDR(addr) printf(" %02x:%02x:%02x:%02x:%02x:%02x ",(*addr)[0], (*addr)[1], (*addr)[2], (*addr)[3], (*addr)[4], (*addr)[5])
#else
#define PRINTETHADDR(addr)
#endif


PROCESS(eth_drv_process, "RAW/TAP Ethernet Driver");

#if UIP_CONF_LLH_LEN == 0
uint8_t ll_header[ETHERNET_LLH_LEN];
#endif

/*---------------------------------------------------------------------------*/

static unsigned char tmp_tap_buf[ETHERNET_LLH_LEN + UIP_BUFSIZE];
void
eth_drv_send(void)
{
  PRINTF
    ("ETH send: %d bytes : %x:%x:%x:%x:%x:%x %x:%x:%x:%x:%x:%x  %x:%x %x %x %x %x %x %x\n",
     uip_len, ll_header[0], ll_header[1], ll_header[2], ll_header[3],
     ll_header[4], ll_header[5], ll_header[6], ll_header[7], ll_header[8],
     ll_header[9], ll_header[10], ll_header[11], ll_header[12], ll_header[13],
     uip_buf[0], uip_buf[1], uip_buf[2], uip_buf[3], uip_buf[4], uip_buf[5]);
  //Should remove ll_header
  memcpy(tmp_tap_buf, ll_header, ETHERNET_LLH_LEN);
  memcpy(tmp_tap_buf + ETHERNET_LLH_LEN, uip_buf, uip_len);
  tun_output(tmp_tap_buf, uip_len + ETHERNET_LLH_LEN);
}
void
eth_drv_exit(void)
{
}

void
eth_drv_init()
{
  PRINTF("RAW/TAP init\n");

  /* tun init is also responsible for setting up the SLIP connection */
  tun_init();
}

/*---------------------------------------------------------------------------*/

PROCESS_THREAD(eth_drv_process, ev, data)
{
  static struct etimer et;

  PROCESS_BEGIN();

  eth_drv_init();
#if !CETIC_6LBR_ONE_ITF
  slip_reboot();
  while(!mac_set) {
    etimer_set(&et, CLOCK_SECOND);
    slip_request_mac();
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));
  }
  //Set radio channel
  slip_set_rf_channel(nvm_data.channel);

  if(!use_raw_ethernet) {
    //We must create our own Ethernet MAC address
    mac_createEthernetAddr((uint8_t *) eth_mac_addr, &wsn_mac_addr);
    eth_mac_addr[0] &= ~TRANSLATE_BIT_MASK;
    PRINTF("Eth MAC address : ");
    PRINTETHADDR(&eth_mac_addr);
    PRINTF("\n");
    eth_mac_addr_ready = 1;
  }
#else
  //TODO: Ethernet Bridge bullshit !
  eth_mac_addr[5] += 1;
  mac_createSicslowpanLongAddr((uint8_t *)eth_mac_addr, &wsn_mac_addr);
  memcpy(uip_lladdr.addr, wsn_mac_addr.addr, sizeof(uip_lladdr.addr));
  rimeaddr_set_node_addr((rimeaddr_t *) &wsn_mac_addr);
  PRINTF("ETH Address : ");
  PRINTLLADDR(&eth_mac_addr);
  PRINTF("\n");
#endif
  ethernet_ready = 1;

  PROCESS_END();
}

/*---------------------------------------------------------------------------*/
