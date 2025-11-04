import styled from 'styled-components';
import black01 from '../../assets/images/2.png';
import "./faq.css";
const SectionWrapper = styled.section`
  min-height: 100vh;
  width: 100vw;
  position: relative; 
  display: flex;
  margin: 0 auto;
  color: white; 
`;


const LeftContainer = styled.div`
  top: 10%;
  left: 5%;
  position: absolute;
  text-transform:uppercase; 
  font-family: boldgod;
`; 

const BannerComponent = styled.div`
  white-space: nowrap;
`;
const Container = styled.div` 
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 40px;
`;

const Faq = () => {
  return (
    <SectionWrapper id="fixed-target" className="faq">
      
      <Container id="up">
      <BannerComponent>
    <img src={black01} className="rick-pic"
      alt="Black NFT artwork"
      data-scroll
      data-scroll-speed="-2"
      data-scroll-direction="horizontal"
      style={{ transform: 'translate3d(0, 0, 0)' }}
          >
          </img>
        </BannerComponent>
      </Container>
      
      <LeftContainer
        data-scroll
        data-scroll-delay=".15"
        data-scroll-speed="1"
        style={{ transform: 'translate3d(0, 0, 0)' }}
      > 
      <section className="accordion">
      <input type="checkbox" name="collapse" id="handle1">
      </input>
      <h2 className="handle">
        <label htmlFor="handle1">How does PreFlight AI know when a flight might be delayed?
          <span className="pl">+</span>
        </label>
      </h2>
      <div class="content">
        <p>
          It continuously monitors MCP Server feeds—departure times, gate status, ATC messages, and weather updates—to generate live delay probabilities for each flight.
        </p>
      </div>
      </section> 
      <section class="accordion">
      <input type="checkbox" name="collapse2" id="handle2">
      </input>
      <h2 class="handle">
        <label for="handle2">Does it tell why a flight is delayed, or just that it will be?
          <span className="pl">+</span>
        </label>
      </h2>
      <div class="content">
        <p>
          Each prediction includes a ranked list of causes — for example crosswinds (+23 %), gate congestion (+17 %), or route propagation (+14 %) — so operations teams can act quickly and confidently.
        </p>
      </div>
      </section> 
      <section class="accordion">
      <input type="checkbox" name="collapse2" id="handle3">
      </input>
      <h2 class="handle">
        <label for="handle3">How does PreFlight AI improve safety?
          <span className="pl">+</span>
        </label>
      </h2>
      <div class="content">
        <p>
          Early delay warnings let dispatchers adjust departure windows or re-assign gates before scheduling conflicts cause operational risk.
        </p>
      </div>
      </section> 
      <section class="accordion">
      <input type="checkbox" name="collapse2" id="handle4">
      </input>
      <h2 class="handle">
        <label for="handle4">What powers PreFlight AI behind the scenes?
          <span className="pl">+</span>
        </label>
      </h2>
      <div class="content">
        <p>
          It runs fully on open-source tools — Langflow for flows, n8n for automation, and locally hosted LLMs via Ollama — keeping your data secure and transparent.
        </p>
      </div>
      </section> 
      <section class="accordion">
      <input type="checkbox" name="collapse2" id="handle5">
      </input>
      <h2 class="handle">
        <label for="handle5">What kind of AI model does it use?
          <span className="pl">+</span>
        </label>
      </h2>
      <div class="content">
        <p>
          A mix of Prophet, XGBoost, and LSTM models analyze flight and weather patterns to forecast delays from minutes to hours ahead.
        </p>
      </div>
      </section> 
      <section class="accordion">
      <input type="checkbox" name="collapse2" id="handle6">
      </input>
      <h2 class="handle">
        <label for="handle6">Can airlines run it locally?
          <span className="pl">+</span>
        </label>
      </h2>
      <div class="content">
        <p>
          Yes — PreFlight AI ships as Docker containers and connects seamlessly to any MCP feed, whether on-premise or cloud.
        </p>
      </div>
      </section>
      </LeftContainer>
    </SectionWrapper>
  );
};

export default Faq;
