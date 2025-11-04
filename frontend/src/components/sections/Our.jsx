import styled from 'styled-components'; 
import "./our.css";
const SectionWrapper = styled.section`
  min-height: 100vh;
  width: 100vw;
  position: relative; 
  display: flex;
  margin: 0 auto;
  color: white; 
`;
const Container = styled.div`
  position: absolute;
  left: 5%;
  top: 35px; 
`; 

const LeftContainer = styled.div`
  position: absolute;
  left: 27%;
  top: -100px;
`; 


const Our = () => {
  return (
    <SectionWrapper id="fixed-target" className="faq">
      
      
      <LeftContainer
        data-scroll
        data-scroll-delay=".15"
        data-scroll-speed="1"
        style={{ transform: 'translate3d(0, 0, 0)' }}
      > 
      <h1 className="our-title">
     <span className="our-yell">Why </span>PreFlight AI </h1>
      
      </LeftContainer>
      <Container
      data-scroll
      data-scroll-delay=".20"
      data-scroll-speed="1"
      style={{ transform: 'translate3d(0, 0, 0)' }}>
      <p className="our-des">
  After years of experience in aviation analytics, the founders of PreFlight AI set out with a vision to make air operations safer, smarter, and more predictable. Even after <br></br>
  building successful flight-ops software for major carriers, their curiosity about using AI for real-time decision-making pushed them further. <br></br>
  <br></br>
  After collaborating with leading engineers and data scientists, the team <span className="make-yell">launched PreFlight AI</span> — an intelligent aviation platform that combines live MCP Server data with predictive modeling. <br></br>
  Within months, it evolved into a system trusted for delay forecasting, weather correlation, and operational transparency. Airlines and flight crews around the world quickly recognized <br></br>
  its value in keeping schedules reliable and passengers informed, inspiring the creators to expand the product even further. <br></br>
  <br></br>
  With a focus on <span className="make-yell">Safety, Predictability, and Explainability</span>, PreFlight AI continues to redefine how aviation teams anticipate issues before they happen — transforming data into clear, actionable insight.
</p>
<br></br>

     
      </Container>
    </SectionWrapper>
  );
};

export default Our;
